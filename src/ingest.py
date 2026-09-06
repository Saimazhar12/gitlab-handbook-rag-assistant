"""
ingest.py
---------
Document loading, chunking, embeddings, and vector storage for the RAG pipeline:
  - Document loading   -> load_documents()
  - Chunking            -> chunk_documents()
  - Embeddings          -> get_embedding_function()
  - Store in ChromaDB   -> build_vectorstore()

Reads cleaned Markdown from data/processed/ (produced by clean.py),
splits each page first by Markdown headers (so a chunk never straddles
two unrelated sections) and then by size (so no chunk is too large for
the embedding model / LLM context), embeds the chunks, and persists
everything to a local Chroma database on disk.

Run this any time data/processed/ changes:
    python src/ingest.py

Requires OPENAI_API_KEY or GOOGLE_API_KEY in your environment / .env
file, depending on EMBEDDING_PROVIDER (see config.py).
"""

import os
import glob
import sys
import time

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from config import (
    PROCESSED_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    get_embedding_function,
)


def parse_frontmatter(raw_text: str):
    """Split a scraped/cleaned .md file into (metadata_dict, body_text)."""
    metadata = {}
    body = raw_text

    if raw_text.startswith("---\n"):
        end = raw_text.find("\n---\n", 4)
        if end != -1:
            fm_block = raw_text[4:end]
            body = raw_text[end + 5 :]
            for line in fm_block.splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip()] = value.strip().strip('"')

    return metadata, body.strip()


def load_documents() -> list[Document]:
    """Document loading.

    Reads every processed .md file and turns it into a single LangChain
    Document carrying the page's metadata (title, source_url, doc_id).
    """
    paths = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.md")))
    if not paths:
        print(f"[error] No processed files found in {PROCESSED_DIR}.")
        print("        Run src/scrape.py then src/clean.py first.")
        sys.exit(1)

    documents = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        metadata, body = parse_frontmatter(raw_text)
        if not body:
            print(f"  [warn] {os.path.basename(path)} has no body content after "
                  f"frontmatter — skipping.")
            continue

        metadata.setdefault("title", os.path.basename(path))
        metadata.setdefault("source_url", "")
        metadata.setdefault("doc_id", os.path.splitext(os.path.basename(path))[0])

        documents.append(Document(page_content=body, metadata=metadata))

    print(f"Loaded {len(documents)} document(s) from {PROCESSED_DIR}")
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Chunking.

    Two-pass split:
      1. MarkdownHeaderTextSplitter groups text under its nearest ##/###
         heading, so a chunk always has topical coherence and we get a
         readable 'section' breadcrumb in metadata for citations.
      2. RecursiveCharacterTextSplitter further splits any section that's
         still too long for a single embedding-friendly chunk.
    """
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Document] = []
    for doc in documents:
        header_sections = header_splitter.split_text(doc.page_content)
        if not header_sections:
            header_sections = [Document(page_content=doc.page_content, metadata={})]

        doc_chunk_index = 0  # sequential across the WHOLE document, not per section
        for section in header_sections:
            sub_chunks = size_splitter.split_documents([section])
            for chunk in sub_chunks:
                # merge: page-level metadata (source_url, title, doc_id)
                # + section-level metadata (h1/h2/h3 from header splitter)
                merged_metadata = {**doc.metadata, **chunk.metadata}
                merged_metadata["chunk_index"] = doc_chunk_index
                doc_chunk_index += 1
                section_path = " > ".join(
                    v for k, v in chunk.metadata.items() if k in ("h1", "h2", "h3") and v
                )
                merged_metadata["section"] = section_path or merged_metadata.get("title", "")
                all_chunks.append(Document(page_content=chunk.page_content, metadata=merged_metadata))

    print(f"Split into {len(all_chunks)} chunk(s) "
          f"(chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP})")

    # Sanity check: fail fast, before spending any API calls, if chunk IDs
    # would collide. Chunk IDs are built from (doc_id, chunk_index), so
    # chunk_index must be unique per document -- this check guards against
    # any future change to the chunking logic accidentally reintroducing
    # duplicate indices.
    seen_ids = set()
    for c in all_chunks:
        cid = f"{c.metadata.get('doc_id', 'doc')}-{c.metadata.get('chunk_index')}"
        if cid in seen_ids:
            print(f"[error] Duplicate chunk id detected: {cid}. "
                  f"Aborting before calling the embeddings API.")
            sys.exit(1)
        seen_ids.add(cid)

    return all_chunks


def build_vectorstore(chunks: list[Document]):
    """Steps 5 & 6: Embeddings + storage in ChromaDB.

    Free-tier Gemini API keys are rate-limited to ~100 embedding requests
    per minute. Sending all chunks in a single call (as Chroma.from_documents
    does internally) blows through that limit on anything but a tiny
    knowledge base. To stay under the limit, we:
      1. Create the Chroma collection empty first.
      2. Add chunks in small batches (BATCH_SIZE at a time).
      3. Pause between batches so we don't exceed ~90 requests/minute.
      4. If a 429 (RESOURCE_EXHAUSTED) still slips through, back off and
         retry that batch instead of crashing the whole run.
    """
    from langchain_chroma import Chroma

    embedding_function = get_embedding_function()

    print(f"Embedding {len(chunks)} chunks and writing to {CHROMA_DIR} "
          f"(collection='{COLLECTION_NAME}')...")

    ids = [
        f"{c.metadata.get('doc_id', 'doc')}-{c.metadata.get('chunk_index', i)}"
        for i, c in enumerate(chunks)
    ]

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DIR,
    )

    BATCH_SIZE = 20          # chunks per API call -- comfortably under free-tier limits
    PAUSE_BETWEEN_BATCHES = 15  # seconds -- keeps us well under ~100 req/min
    MAX_RETRIES = 5

    total = len(chunks)
    for batch_start in range(0, total, BATCH_SIZE):
        batch_docs = chunks[batch_start: batch_start + BATCH_SIZE]
        batch_ids = ids[batch_start: batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                vectorstore.add_documents(documents=batch_docs, ids=batch_ids)
                print(f"  [ok] batch {batch_num}/{total_batches} "
                      f"({len(batch_docs)} chunks) embedded")
                break
            except Exception as exc:
                is_rate_limit = "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc)
                if is_rate_limit and attempt < MAX_RETRIES:
                    wait = 40 * attempt
                    print(f"  [warn] rate limited on batch {batch_num} "
                          f"(attempt {attempt}/{MAX_RETRIES}) -- waiting {wait}s...")
                    time.sleep(wait)
                    continue
                raise

        if batch_start + BATCH_SIZE < total:
            time.sleep(PAUSE_BETWEEN_BATCHES)

    print(f"[ok] Vectorstore ready with {vectorstore._collection.count()} chunk(s).")
    return vectorstore


def main():
    documents = load_documents()
    chunks = chunk_documents(documents)
    build_vectorstore(chunks)
    print("\nIngestion complete. You can now run:")
    print("  streamlit run app.py")
    print("  python evaluate.py")


if __name__ == "__main__":
    main()
