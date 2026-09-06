"""
rag_chain.py
------------
Retrieval, LLM connection, and answer generation with citations:
  - Retrieval                        -> retrieve()
  - Connecting the LLM                -> config.get_chat_model()
  - Generating answers with citations -> answer_question()

Citations are NOT left to the LLM to invent. We build the source list
ourselves from the metadata of the chunks that were actually retrieved
and actually used in the prompt, then append it to the model's answer.
This is more reliable for a demo than trusting the model to accurately
report which of its training-data-adjacent "memories" vs. the provided
context it used.
"""

import os
from dataclasses import dataclass, field

from config import CHROMA_DIR, COLLECTION_NAME, RETRIEVAL_K, MAX_RELEVANT_DISTANCE, get_embedding_function, get_chat_model

SYSTEM_PROMPT = """You are the SafeX Solutions Handbook Assistant, a support bot that \
answers questions using ONLY the GitLab Handbook excerpts provided below as context.

Rules:
- Answer using only the information in the context. Do not use outside knowledge.
- If the context does not contain enough information to answer, say clearly that \
you don't have that information in the available handbook pages -- do not guess \
or make anything up.
- Be concise and direct. Use bullet points for lists.
- Do not include a "Sources" section yourself -- it will be added automatically \
after your answer.

Context:
{context}
"""


@dataclass
class RagResult:
    answer: str
    sources: list = field(default_factory=list)   # list of dicts: title, source_url, section
    used_fallback: bool = False


def _format_context(chunks_with_scores) -> str:
    parts = []
    for i, (doc, score) in enumerate(chunks_with_scores, start=1):
        parts.append(
            f"[Excerpt {i} | {doc.metadata.get('title', 'Unknown')} "
            f"> {doc.metadata.get('section', '')}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def _dedupe_sources(chunks_with_scores) -> list:
    seen = set()
    sources = []
    for doc, _score in chunks_with_scores:
        key = doc.metadata.get("source_url", "") or doc.metadata.get("doc_id", "")
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "title": doc.metadata.get("title", "Unknown"),
            "source_url": doc.metadata.get("source_url", ""),
            "section": doc.metadata.get("section", ""),
        })
    return sources


def _extract_text(content) -> str:
    """Normalize LLM response content to a plain string.

    Newer Gemini models (and recent LangChain versions) may return
    `response.content` as a list of structured content blocks --
    e.g. [{"type": "text", "text": "...", "extras": {"signature": "..."}}]
    -- instead of a plain string. This unwraps that safely so the rest
    of the app always deals with plain text.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and "text" in block:
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts) if parts else str(content)
    return str(content)


class RagChatbot:
    def __init__(self):
        self.vectorstore = self._load_vectorstore()
        self.llm = get_chat_model()

    def _load_vectorstore(self):
        from langchain_chroma import Chroma

        if not os.path.isdir(CHROMA_DIR):
            raise RuntimeError(
                f"No Chroma database found at '{CHROMA_DIR}'. "
                f"Run `python src/ingest.py` first to build it."
            )
        embedding_function = get_embedding_function()
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_function,
            persist_directory=CHROMA_DIR,
        )
        if vectorstore._collection.count() == 0:
            raise RuntimeError(
                "The Chroma collection is empty. Run `python src/ingest.py` first."
            )
        return vectorstore

    def retrieve(self, query: str, k: int = RETRIEVAL_K):
        """Step 7: Retrieval. Returns [(Document, distance_score), ...]."""
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results

    def answer_question(self, query: str) -> RagResult:
        """Steps 8-9: Connect the LLM and generate a cited answer."""
        query = (query or "").strip()

        # --- Edge case: empty input ---
        if not query:
            return RagResult(
                answer="Please enter a question.",
                sources=[],
                used_fallback=True,
            )

        # --- Edge case: input too long (guard against runaway prompts/cost) ---
        MAX_QUERY_CHARS = 1000
        if len(query) > MAX_QUERY_CHARS:
            query = query[:MAX_QUERY_CHARS]

        try:
            chunks_with_scores = self.retrieve(query)
        except Exception as exc:
            return RagResult(
                answer=f"Sorry, I couldn't search the knowledge base right now "
                       f"({type(exc).__name__}). Please try again in a moment.",
                sources=[],
                used_fallback=True,
            )

        if not chunks_with_scores:
            return RagResult(
                answer="I don't have any information about that in the handbook "
                       "pages I have access to.",
                sources=[],
                used_fallback=True,
            )

        # --- Edge case: nothing retrieved is actually relevant ---
        relevant = [(d, s) for d, s in chunks_with_scores if s <= MAX_RELEVANT_DISTANCE]
        if not relevant:
            return RagResult(
                answer="I don't have information about that in the GitLab Handbook "
                       "pages I've been given (Mission, Values, Communication, Remote "
                       "Work, Diversity & Inclusion, Hiring, Compensation, "
                       "Security, Leadership, Career Development, Engineering, Open "
                       "Source, and Learning & Development). Try rephrasing, or ask "
                       "about one of those topics.",
                sources=[],
                used_fallback=True,
            )

        context = _format_context(relevant)
        sources = _dedupe_sources(relevant)

        try:
            messages = [
                ("system", SYSTEM_PROMPT.format(context=context)),
                ("human", query),
            ]
            response = self.llm.invoke(messages)
            answer_text = _extract_text(response.content)
        except Exception as exc:
            return RagResult(
                answer=f"Sorry, the language model is unavailable right now "
                       f"({type(exc).__name__}). Please check your API key/quota "
                       f"and try again.",
                sources=[],
                used_fallback=True,
            )

        return RagResult(answer=answer_text, sources=sources, used_fallback=False)


def format_answer_with_citations(result: RagResult) -> str:
    """CLI/plain-text formatting helper: answer + numbered source list."""
    text = result.answer
    if result.sources:
        text += "\n\nSources:\n"
        for i, src in enumerate(result.sources, start=1):
            section = f" — {src['section']}" if src.get("section") else ""
            text += f"  [{i}] {src['title']}{section}\n      {src['source_url']}\n"
    return text


if __name__ == "__main__":
    bot = RagChatbot()
    print("SafeX Handbook Assistant (CLI mode). Type 'exit' to quit.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = bot.answer_question(q)
        print("\nBot:", format_answer_with_citations(result), sep="\n")
        print()
