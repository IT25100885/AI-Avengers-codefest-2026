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
    search_steps = []
    accumulated_evidence: list[dict] = []
    previous_queries: list[str] = []

    query = plan_initial_query(question)

    for round_num in range(1, MAX_ROUNDS + 1):
        previous_queries.append(query)
        results = search(query, top_k=TOP_K)
        accumulated_evidence = _dedupe(accumulated_evidence + results)

        check = check_sufficiency(question, accumulated_evidence)
        status = check["status"]

        search_steps.append({
            "round": round_num,
            "query": query,
            "sources_found": len(results),
            "status": status,
        })

        if status == "sufficient" or round_num == MAX_ROUNDS:
            break

        query = rewrite_query(question, check["missing_information"], previous_queries)

    answer_text = generate_answer(question, accumulated_evidence)

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
