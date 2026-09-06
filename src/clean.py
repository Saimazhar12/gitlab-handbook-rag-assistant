"""
clean.py
--------
Data cleaning and preprocessing for the RAG pipeline.

Takes the raw scraped Markdown in data/raw/ and produces cleaned
versions in data/processed/, ready for chunking. This step is kept
separate from scrape.py deliberately: scraping is slow/network-bound
and shouldn't need to be re-run every time you tweak a cleaning rule.

Cleaning applied here:
  1. Strip GitLab handbook boilerplate lines ("Last modified...",
     "View page source", "Edit this page", "please contribute.",
     license footer, "On This Page" leftovers).
  2. Collapse excessive blank lines / whitespace.
  3. Drop markdown link syntax noise where it hurts embedding quality
     (keep the link text, drop the raw URL) -- links are still
     recoverable from source_url metadata for citations.
  4. Remove duplicate consecutive lines (common artifact of nav menus
     that weren't fully stripped by the HTML selectors).
  5. Enforce a minimum content length -- flags pages that scraped
     almost nothing so you can fix the scraper instead of silently
     ingesting an empty document.

Usage:
    python src/clean.py
"""

import os
import re
import glob

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

MIN_CONTENT_CHARS = 300

BOILERPLATE_PATTERNS = [
    r"^Last modified .+$",
    r"^View page source.*$",
    r"^Edit this page.*$",
    r".*please contribute\.?$",
    r"^Creative Commons License$",
    r"^© \d{4} GitLab.*$",
    r"^Privacy Statement.*Cookie Settings.*$",
    r"^On This Page$",
    r"^Maintainers?$",
]
BOILERPLATE_RE = re.compile("|".join(BOILERPLATE_PATTERNS), re.IGNORECASE)

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((?:https?://[^\)]+|/[^\)]+)\)")


def split_frontmatter(text: str):
    """Return (frontmatter_str_including_delimiters, body_str)."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            frontmatter = text[: end + 5]
            body = text[end + 5 :]
            return frontmatter, body
    return "", text


def strip_boilerplate(body: str) -> str:
    lines = body.splitlines()
    kept = [ln for ln in lines if not BOILERPLATE_RE.match(ln.strip())]
    return "\n".join(kept)


def collapse_markdown_links(body: str) -> str:
    """Keep link text, drop the raw URL -- reduces noise for embeddings."""
    return MARKDOWN_LINK_RE.sub(r"\1", body)


def dedupe_consecutive_lines(body: str) -> str:
    lines = body.splitlines()
    deduped = []
    prev = None
    for ln in lines:
        if ln.strip() == "" or ln != prev:
            deduped.append(ln)
        prev = ln
    return "\n".join(deduped)


def collapse_blank_lines(body: str) -> str:
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def clean_body(body: str) -> str:
    body = strip_boilerplate(body)
    body = collapse_markdown_links(body)
    body = dedupe_consecutive_lines(body)
    body = collapse_blank_lines(body)
    return body


def process_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    frontmatter, body = split_frontmatter(raw_text)
    cleaned_body = clean_body(body)

    status = "ok"
    if len(cleaned_body) < MIN_CONTENT_CHARS:
        status = "warn_short"

    filename = os.path.basename(path)
    out_path = os.path.join(PROCESSED_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + cleaned_body)

    return {
        "file": filename,
        "status": status,
        "raw_chars": len(raw_text),
        "cleaned_chars": len(cleaned_body),
    }


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.md")))

    if not raw_files:
        print(f"No raw .md files found in {RAW_DIR}. Run src/scrape.py first.")
        return

    print(f"Cleaning {len(raw_files)} file(s)...\n")
    results = [process_file(p) for p in raw_files]

    print(f"{'file':40s} {'status':10s} {'raw':>8s} {'cleaned':>8s}")
    for r in results:
        print(f"{r['file']:40s} {r['status']:10s} {r['raw_chars']:8d} {r['cleaned_chars']:8d}")

    warnings = [r for r in results if r["status"] != "ok"]
    if warnings:
        print(f"\n[warn] {len(warnings)} file(s) have suspiciously little content "
              f"after cleaning (< {MIN_CONTENT_CHARS} chars). Inspect them before "
              f"chunking/embedding -- the scraper may have grabbed the wrong container "
              f"for that page's layout.")
    else:
        print("\nAll files cleaned successfully.")


if __name__ == "__main__":
    main()
