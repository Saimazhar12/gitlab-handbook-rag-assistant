"""
scrape.py
---------
Collecting the documents for the RAG pipeline.

Fetches each URL in sources.py, extracts the main article content
(stripping site navigation, sidebars, and footers), converts it to
Markdown, and writes one .md file per page into data/raw/.

Each output file starts with a small YAML front-matter block so that
downstream steps (loading/chunking) can carry metadata --
particularly `source_url`, which is what powers citations later in
the chatbot.

Usage:
    python src/scrape.py

Requires (see requirements.txt):
    requests, beautifulsoup4, markdownify
"""

import os
import sys
import time
import datetime
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from sources import SOURCES

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
HEADERS = {
    "User-Agent": (
        "SafeXSolutions-Internship-RAGBot/1.0 "
        "(educational project; contact: intern@example.com)"
    )
}
REQUEST_TIMEOUT = 15
RETRY_COUNT = 3
RETRY_BACKOFF_SECONDS = 2


def fetch_html(url: str) -> str:
    """Fetch a URL with retries. Raises the last exception if all retries fail."""
    last_exc = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
            print(f"  [warn] attempt {attempt}/{RETRY_COUNT} failed for {url}: {exc}")
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Failed to fetch {url} after {RETRY_COUNT} attempts") from last_exc


def extract_main_content(html: str) -> BeautifulSoup:
    """
    Extract the main article content from a handbook.gitlab.com page.

    The GitLab Handbook is a Hugo static site. The article body lives in
    a <main> or <article> tag; navigation, the left-hand tree menu, and
    the footer ("View page source", "Last modified...", license notice)
    are siblings we want to discard.
    """
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find("article") or soup.find("main") or soup.find(
        "div", class_="td-content"
    )
    if content is None:
        # Fall back to the whole body if the expected containers aren't found;
        # downstream cleaning will strip obvious boilerplate lines.
        content = soup.body or soup

    # Remove elements that are clearly not article content.
    unwanted_selectors = [
        "nav",
        "footer",
        "script",
        "style",
        {"class": "td-page-meta"},   # "View page source / Edit this page"
        {"class": "td-breadcrumbs"},
        {"class": "feedback"},
        {"class": "td-toc"},         # right-hand "On This Page" mini-TOC
    ]
    for sel in unwanted_selectors:
        if isinstance(sel, str):
            for tag in content.find_all(sel):
                tag.decompose()
        else:
            for tag in content.find_all(attrs=sel):
                tag.decompose()

    return content


def html_to_markdown(content_soup: BeautifulSoup) -> str:
    markdown = md(str(content_soup), heading_style="ATX")
    return markdown


def clean_markdown(markdown: str) -> str:
    """Light structural cleanup applied at scrape time (deeper cleaning happens in clean.py)."""
    lines = [line.rstrip() for line in markdown.splitlines()]

    # Collapse 3+ consecutive blank lines down to 1.
    cleaned_lines = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines).strip() + "\n"
    return text


def build_frontmatter(name: str, title: str, url: str) -> str:
    scraped_at = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    return (
        "---\n"
        f"title: \"{title}\"\n"
        f"source_url: \"{url}\"\n"
        f"scraped_at: \"{scraped_at}\"\n"
        f"doc_id: \"{name}\"\n"
        "---\n\n"
    )


def scrape_one(source: dict) -> bool:
    name, title, url = source["name"], source["title"], source["url"]
    print(f"Scraping: {title} ({url})")
    try:
        html = fetch_html(url)
    except Exception as exc:
        print(f"  [error] giving up on {url}: {exc}")
        return False

    content_soup = extract_main_content(html)
    markdown_body = html_to_markdown(content_soup)
    markdown_body = clean_markdown(markdown_body)

    if len(markdown_body) < 200:
        print(f"  [warn] extracted content looks too short ({len(markdown_body)} chars) — "
              f"check extract_main_content() selectors for this page.")

    frontmatter = build_frontmatter(name, title, url)
    out_path = os.path.join(RAW_DIR, f"{name}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + markdown_body)

    print(f"  [ok] saved -> {out_path} ({len(markdown_body)} chars)")
    return True


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    results = {"ok": 0, "failed": []}

    for source in SOURCES:
        success = scrape_one(source)
        if success:
            results["ok"] += 1
        else:
            results["failed"].append(source["url"])
        time.sleep(1)  # be polite to the server

    print("\n--- Scrape summary ---")
    print(f"Succeeded: {results['ok']}/{len(SOURCES)}")
    if results["failed"]:
        print("Failed URLs (retry manually or update sources.py):")
        for u in results["failed"]:
            print(f"  - {u}")
        sys.exit(1)


if __name__ == "__main__":
    main()
