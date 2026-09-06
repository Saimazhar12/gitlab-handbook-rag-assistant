"""
evaluate.py
-----------
Evaluation with test questions.

Runs a fixed set of 20 test questions through the chatbot and reports:
  1. Retrieval accuracy  -- did the expected source page appear among
     the retrieved chunks for that question? (automatic, objective)
  2. The generated answer + citations for each question, saved to a
     Markdown report for manual review (fluency, correctness, whether
     it appropriately refuses out-of-scope questions).

Includes a mix of:
  - Straightforward in-scope questions (one per source page, 14 total)
  - Cross-page questions that could draw from multiple pages
  - Out-of-scope / adversarial questions the bot SHOULD refuse

Usage:
    python evaluate.py
Output:
    data/eval_report.md
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag_chain import RagChatbot, format_answer_with_citations  # noqa: E402

REPORT_PATH = os.path.join(os.path.dirname(__file__), "data", "eval_report.md")

# Each test case: question, and the doc_id we EXPECT to be retrieved.
# expected_doc_id = None means "out of scope" -- we expect a fallback/refusal,
# not a real citation.
TEST_CASES = [
    {"question": "What is GitLab's mission?", "expected_doc_id": "mission"},
    {"question": "What are GitLab's core values?", "expected_doc_id": "values"},
    {"question": "What is the purpose of the GitLab handbook?", "expected_doc_id": "about-the-handbook"},
    {"question": "How does GitLab prefer teams to communicate, synchronously or asynchronously?", "expected_doc_id": "communication"},
    {"question": "What does it mean for GitLab to be an all-remote company?", "expected_doc_id": "remote-work-guide"},
    {"question": "How does GitLab approach diversity, inclusion, and belonging?", "expected_doc_id": "diversity-inclusion-belonging"},
    {"question": "What does GitLab's hiring process look like?", "expected_doc_id": "hiring"},
    {"question": "How does GitLab decide employee compensation?", "expected_doc_id": "compensation"},
    {"question": "What security practices does GitLab follow?", "expected_doc_id": "security-practices"},
    {"question": "What does GitLab expect from its leaders?", "expected_doc_id": "leadership"},
    {"question": "How can employees grow their careers at GitLab?", "expected_doc_id": "career-development"},
    {"question": "What does the Development department at GitLab do?", "expected_doc_id": "development-department"},
    {"question": "How does GitLab engage with open source contributors?", "expected_doc_id": "open-source"},
    {"question": "What learning and development resources does GitLab offer employees?", "expected_doc_id": "learning-and-development"},
    # Cross-page / broader questions
    {"question": "How does GitLab support employees working across many different time zones?", "expected_doc_id": None},
    {"question": "How does GitLab's culture support both transparency and career growth?", "expected_doc_id": None},
    {"question": "What does GitLab expect from managers versus individual contributors?", "expected_doc_id": None},
    # Out-of-scope / adversarial -- bot should refuse, not hallucinate
    {"question": "What is the weather like in Lahore today?", "expected_doc_id": None},
    {"question": "What was GitLab's exact stock price on July 4th, 2024?", "expected_doc_id": None},
]


def check_retrieval_hit(bot: RagChatbot, question: str, expected_doc_id: str) -> bool:
    if expected_doc_id is None:
        return True  # nothing specific expected; not scored for retrieval
    chunks_with_scores = bot.retrieve(question, k=4)
    retrieved_doc_ids = {doc.metadata.get("doc_id") for doc, _ in chunks_with_scores}
    return expected_doc_id in retrieved_doc_ids


def main():
    print("Loading chatbot...")
    try:
        bot = RagChatbot()
    except Exception as exc:
        print(f"[error] Could not load chatbot: {exc}")
        print("        Run src/scrape.py, src/clean.py, then src/ingest.py first.")
        sys.exit(1)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    scored_cases = [tc for tc in TEST_CASES if tc["expected_doc_id"] is not None]
    hits = 0
    report_lines = ["# Evaluation Report\n"]

    for i, case in enumerate(TEST_CASES, start=1):
        question = case["question"]
        expected = case["expected_doc_id"]
        print(f"[{i}/{len(TEST_CASES)}] {question}")

        hit = check_retrieval_hit(bot, question, expected)
        if expected is not None:
            hits += int(hit)

        result = bot.answer_question(question)

        report_lines.append(f"## {i}. {question}\n")
        report_lines.append(f"**Expected source:** `{expected or 'none / out-of-scope'}`  ")
        if expected is not None:
            report_lines.append(f"**Retrieval hit:** {'✅ yes' if hit else '❌ no'}\n")
        else:
            report_lines.append("**Retrieval hit:** _not scored (open-ended/out-of-scope)_\n")
        report_lines.append("**Answer:**\n")
        report_lines.append(f"> {result.answer}\n")
        if result.sources:
            src_lines = [f"- {s['title']} — {s['source_url']}" for s in result.sources]
            report_lines.append("**Cited sources:**\n" + "\n".join(src_lines) + "\n")
        else:
            report_lines.append("**Cited sources:** _none (fallback response)_\n")
        report_lines.append("---\n")

        time.sleep(0.5)  # be gentle on API rate limits

    accuracy = hits / len(scored_cases) if scored_cases else 0.0
    summary = (
        f"\n## Summary\n\n"
        f"Retrieval accuracy: **{hits}/{len(scored_cases)} "
        f"({accuracy:.0%})** on questions with a known expected source.\n\n"
        f"Note: retrieval accuracy is automatic and objective (did the right "
        f"page get retrieved). Answer *quality* (fluency, correctness, "
        f"appropriate refusals on out-of-scope questions) still needs a quick "
        f"manual read-through of this report — that's expected for an LLM "
        f"system.\n"
    )
    report_lines.append(summary)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\nDone. Retrieval accuracy: {hits}/{len(scored_cases)} ({accuracy:.0%})")
    print(f"Full report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
