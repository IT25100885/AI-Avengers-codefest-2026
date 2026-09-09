"""
The full iterative Track 1C search loop.

Place this at: src/agent/search_agent.py

Implements answer_question(question) -> dict matching the team's agreed
evaluation-harness output contract:

{
  "answer": "...",
  "search_steps": [
    {
      "round": 1,
      "query": "...",
      "sources_found": 8,
      "status": "insufficient"
    },
    {
      "round": 2,
      "query": "...",
      "sources_found": 5,
      "status": "sufficient"
    }
  ],
  "sources": [
    {
      "source": "codex.pdf",
      "page": 17
    }
  ]
}
"""

import os
from typing import Optional

from src.agent.planner import plan_initial_query
from src.agent.evidence_checker import check_sufficiency
from src.agent.query_rewriter import rewrite_query
from src.generation.answer_generator import generate_answer

# REAL retrieval pipeline:
# Voyage query embedding -> ChromaDB -> Voyage reranking
from src.retrieval.search import search


MAX_ROUNDS = int(os.getenv("MAX_SEARCH_ROUNDS", 3))
TOP_K = int(os.getenv("SEARCH_TOP_K", 15))


def _dedupe(evidence_list: list[dict]) -> list[dict]:
    """
    Remove duplicate evidence chunks using chunk_id.
    """
    seen = set()
    unique = []

    for evidence in evidence_list:
        chunk_id = evidence.get("chunk_id")

        if chunk_id not in seen:
            seen.add(chunk_id)
            unique.append(evidence)

    return unique


def answer_question(
    question: str,
    max_rounds: Optional[int] = None,
    top_k: Optional[int] = None,
) -> dict:
    """
    Answer a question using iterative multi-round search.

    Steps:
    1. Plan initial search query.
    2. Search the indexed Ashen Era Archive.
    3. Accumulate retrieved evidence.
    4. Check whether evidence is sufficient.
    5. Rewrite the query if information is missing.
    6. Repeat until evidence is sufficient or the maximum
       number of rounds is reached.
    7. Generate a grounded final answer.
    """

    if not question or not question.strip():
        return {
            "answer": (
                "No question was provided. "
                "Please enter an inquiry to search the archive."
            ),
            "search_steps": [],
            "sources": [],
        }

    cleaned_question = question.strip()

    effective_max_rounds = (
        max_rounds
        if max_rounds is not None
        else int(os.getenv("MAX_SEARCH_ROUNDS", 3))
    )

    effective_top_k = (
        top_k
        if top_k is not None
        else int(os.getenv("SEARCH_TOP_K", 15))
    )

    search_steps = []
    accumulated_evidence: list[dict] = []
    previous_queries: list[str] = []

    # ---------------------------------------------------------
    # Round 1: Initial search planning
    # ---------------------------------------------------------
    query = plan_initial_query(cleaned_question)

    # ---------------------------------------------------------
    # Iterative Track 1C search loop
    # ---------------------------------------------------------
    for round_num in range(1, effective_max_rounds + 1):

        previous_queries.append(query)

        # Search REAL indexed Ashen Era Archive
        results = search(
            query,
            top_k=effective_top_k,
        )

        # Accumulate evidence across search rounds
        accumulated_evidence = _dedupe(
            accumulated_evidence + results
        )

        # Determine whether enough evidence has been collected
        check = check_sufficiency(
            cleaned_question,
            accumulated_evidence,
        )

        status = check.get("status", "insufficient")
        missing_information = check.get(
            "missing_information",
            "",
        )

        search_steps.append(
            {
                "round": round_num,
                "query": query,
                "sources_found": len(results),
                "status": status,
                "missing_info": missing_information,
            }
        )

        # Stop if enough evidence was found
        if status == "sufficient":
            break

        # Stop when maximum round budget is reached
        if round_num == effective_max_rounds:
            break

        # Otherwise generate a better search query
        query = rewrite_query(
            cleaned_question,
            missing_information,
            previous_queries,
        )

    # ---------------------------------------------------------
    # Generate final grounded answer
    # ---------------------------------------------------------
    answer_text = generate_answer(
        cleaned_question,
        accumulated_evidence,
    )

    # ---------------------------------------------------------
    # Build citation/source list
    # ---------------------------------------------------------
    sources = []

    for evidence in accumulated_evidence:
        sources.append(
            {
                "source": evidence.get(
                    "source",
                    "unknown",
                ),
                "page": evidence.get("page"),
                "category": evidence.get(
                    "category",
                    "unknown",
                ),
            }
        )

    # Remove duplicate citations by source + page
    seen_sources = set()
    unique_sources = []

    for source in sources:
        key = (
            source["source"],
            source["page"],
        )

        if key not in seen_sources:
            seen_sources.add(key)
            unique_sources.append(source)

    return {
        "answer": answer_text,
        "search_steps": search_steps,
        "sources": unique_sources,
    }


if __name__ == "__main__":
    import json

    question = (
        "Which war was won by the organization that included "
        "Isolde Mournvale as one of its members?"
    )

    result = answer_question(question)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )