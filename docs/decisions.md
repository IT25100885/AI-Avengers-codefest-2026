## LLM model selection (Groq) — [today's date] — Abdullah

Initially configured for `llama-3.3-70b-versatile`, which returned a 404
(model no longer available on our account). Queried Groq's /v1/models
endpoint directly to get the real list of accessible models, and switched
to `openai/gpt-oss-120b` for stronger multi-hop reasoning and reliable
structured JSON output, needed for the evidence-sufficiency checker.
Verified with both a plain text call and a structured JSON call before
proceeding.

## LLM model selection (Groq)
Initially configured for `llama-3.3-70b-versatile`, which returned a 404
(model no longer available on our account). Queried Groq's /v1/models
endpoint directly to get the real list of accessible models, and switched
to `openai/gpt-oss-120b` for stronger multi-hop reasoning and reliable
structured JSON output, needed for the evidence-sufficiency checker.
Verified with both a plain text call and a structured JSON call before
proceeding.

## Planner query scope (Day 3)
Initial version of the planner produced broad first-round queries
(e.g. "Isolde Mournvale organization war won"), which caused the mock
search to retrieve all relevant chunks in a single round -- making the
system behave like basic RAG instead of demonstrating genuine iterative
search, as required by Track 1C. Fixed by narrowing the planner's prompt
to extract only the primary named entity for round 1, deferring secondary
concepts (war, victory, faction) to the query rewriter in later rounds.
Verified: the same test question now correctly triggers 2 search rounds,
with round 1 marked insufficient and round 2 marked sufficient.
