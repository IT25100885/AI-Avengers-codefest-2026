"""
The full iterative Track 1C search loop.

Place this at: src/agent/search_agent.py

Implements answer_question(question) -> dict matching the team's agreed
evaluation-harness output contract:

{
  "answer": "...",
  "search_steps": [
    {"round": 1, "query": "...", "sources_found": 8, "status": "insufficient"},
    {"round": 2, "query": "...", "sources_found": 5, "status": "sufficient"}
  ],
  "sources": [{"source": "codex.pdf", "page": 17}]
}
"""

import os

from src.agent.planner import plan_initial_query
from src.agent.evidence_checker import check_sufficiency
from src.agent.query_rewriter import rewrite_query
from src.generation.answer_generator import generate_answer
from src.retrieval.mock_search import search

MAX_ROUNDS = int(os.getenv("MAX_SEARCH_ROUNDS", 3))
TOP_K = int(os.getenv("SEARCH_TOP_K", 15))


def _dedupe(evidence_list: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for e in evidence_list:
        if e["chunk_id"] not in seen:
            seen.add(e["chunk_id"])
            unique.append(e)
    return unique


def answer_question(question: str) -> dict:
    cleaned_question = question.strip() if question else ""
    if not cleaned_question or not any(c.isalnum() for c in cleaned_question):
        return {
            "answer": "Please provide a valid question about the Ashen Era Archive.",
            "search_steps": [],
            "sources": [],
        }

    search_steps = []
    accumulated_evidence: list[dict] = []
    previous_queries: list[str] = []

    query = plan_initial_query(cleaned_question)
    if not query.strip():
        query = cleaned_question

    for round_num in range(1, MAX_ROUNDS + 1):
        # Stop condition: prevent repeating duplicate search queries
        normalized_query = query.strip().lower()
        if normalized_query in [q.strip().lower() for q in previous_queries]:
            break

        previous_queries.append(query)
        results = search(query, top_k=TOP_K)
        accumulated_evidence = _dedupe(accumulated_evidence + results)

        check = check_sufficiency(cleaned_question, accumulated_evidence)
        status = check["status"]

        search_steps.append({
            "round": round_num,
            "query": query,
            "sources_found": len(results),
            "status": status,
        })

        if status == "sufficient" or round_num == MAX_ROUNDS:
            break

        # Stop condition: if 2 consecutive rounds yielded 0 total evidence, stop to prevent query drift
        if round_num >= 2 and len(accumulated_evidence) == 0:
            break

        next_query = rewrite_query(cleaned_question, check["missing_information"], previous_queries)
        if not next_query.strip() or next_query.strip().lower() in [q.strip().lower() for q in previous_queries]:
            # Stop condition: rewriter cannot formulate a new distinct query
            break

        query = next_query

    answer_text = generate_answer(cleaned_question, accumulated_evidence)

    sources = [
        {"source": e["source"], "page": e.get("page")}
        for e in accumulated_evidence
    ]
    # dedupe sources by (source, page)
    seen_sources = set()
    unique_sources = []
    for s in sources:
        key = (s["source"], s["page"])
        if key not in seen_sources:
            seen_sources.add(key)
            unique_sources.append(s)

    return {
        "answer": answer_text,
        "search_steps": search_steps,
        "sources": unique_sources,
    }


if __name__ == "__main__":
    import json

    q = "Which war was won by the organization that included Isolde Mournvale as one of its members?"
    result = answer_question(q)
    print(json.dumps(result, indent=2))
