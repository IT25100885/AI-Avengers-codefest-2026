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

Return ONLY the new query text, nothing else."""


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
    cleaned = query.replace('"', '').replace("'", "")
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', cleaned)
    return cleaned.strip()
