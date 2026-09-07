"""
Query rewriter: given what's missing, produce a NEW search query that targets
the gap -- not a repeat of a previous query.

Place this at: src/agent/query_rewriter.py
"""
import re

from src.llm.client import call_llm


REWRITER_SYSTEM_PROMPT = """You generate the NEXT search query for an iterative research
assistant searching a fantasy document archive.

You will be given the original question, what information is still missing, and the
list of queries already tried. Produce a new, short, keyword-style search query that
specifically targets the missing information. It must be meaningfully different from
every previously tried query -- do not just repeat or lightly reword them.

Return ONLY the new query text as a single line, nothing else -- do not repeat phrases."""


def rewrite_query(question: str, missing_info: str, previous_queries: list[str]) -> str:
    previous_text = "\n".join(f"- {q}" for q in previous_queries) or "(none yet)"
    messages = [
        {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Original question: {question}\n"
            f"Missing information: {missing_info}\n"
            f"Previously tried queries:\n{previous_text}\n\n"
            "New search query:"
        )},
    ]
    query = call_llm(messages, temperature=0.3)

    # Take the first non-empty line in case model outputs multi-line responses
    lines = [line.strip() for line in query.splitlines() if line.strip()]
    raw_text = lines[0] if lines else ""

    cleaned = raw_text.replace('"', '').replace("'", "")
    # Strip non-whitespace control characters, normalize whitespace
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Deduplicate exact repeated concatenated phrases (e.g. PhrasePhrase -> Phrase)
    dup_match = re.match(r"^(.{8,}?)\1+$", cleaned)
    if dup_match:
        cleaned = dup_match.group(1).strip()

    return cleaned
