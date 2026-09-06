# Technical Decisions

## Decision 001: Evaluation scoring system

Date: 2026-09-04

Decision:
Use a 0-2 scoring scale for retrieval, answer quality, citations,
and iterative search behaviour.

Reason:
The scale is simple enough for rapid testing while still separating
failed, partial, and successful results.

Alternatives considered:
- Pass/fail scoring
- A 1-5 scoring scale

Status:
Accepted

## Decision 002: LLM model selection (Groq)

Date: 2026-09-06

Decision:
Initially configured for `llama-3.3-70b-versatile`, which returned a 404
(model no longer available on our account). Queried Groq's /v1/models
endpoint directly to get the real list of accessible models, and switched
to `openai/gpt-oss-120b` for stronger multi-hop reasoning and reliable
structured JSON output, needed for the evidence-sufficiency checker.
Verified with both a plain text call and a structured JSON call before
proceeding.

Status:
Accepted

## Decision 003: Planner query scope

Date: 2026-09-06

Decision:
Narrow the planner's prompt to extract only the primary named entity for round 1, deferring secondary concepts (war, victory, faction) to the query rewriter in later rounds.

Reason:
Initial version of the planner produced broad first-round queries
(e.g. "Isolde Mournvale organization war won"), which caused the mock
search to retrieve all relevant chunks in a single round -- making the
system behave like basic RAG instead of demonstrating genuine iterative
search, as required by Track 1C. Fixed by narrowing the planner's prompt
to extract only the primary named entity for round 1, deferring secondary
concepts (war, victory, faction) to the query rewriter in later rounds.
Verified: the same test question now correctly triggers 2 search rounds,
with round 1 marked insufficient and round 2 marked sufficient.

Status:
Accepted
