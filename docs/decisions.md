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

## Decision 004: Streamlit UI architecture, dual-backend toggle, and search step transparency

Date: 2026-09-07 (Updated: 2026-09-08)

Decision:
Build an interactive Streamlit UI (`src/app.py`) incorporating:
1. Visual multi-round execution cards displaying round number, reformulated query, retrieved source count, and sufficiency status badges (`Sufficient` / `Insufficient`).
2. A dual-backend architecture with a sidebar selector:
   - "Simulation Mode (Offline / Competition Demo)": Guarantees instant, deterministic multi-round responses for official benchmark questions without external API keys or network latency.
   - "Live Agent Pipeline": Directly connects to Member 2's `src.agent.search_agent.answer_question` for real-time model inference.
3. Strict operational boundaries:
   - No automatic fallback: If the live agent fails (e.g. missing API keys or rate limits), the error is displayed transparently rather than silently falling back to mock data.
   - Strict simulation scope: Arbitrary questions entered in simulation mode return an explicit refusal ("No simulation available for this question") rather than invented lore or fake traces.
   - Explicit labeling: Every simulated answer visibly declares it is a pre-recorded benchmark demonstration, including in session history.
4. Parameter coordination: Sidebar sliders for Max Search Rounds and Top-K retrieval are dynamically passed to `answer_question(question, max_rounds, top_k)` in live mode, and disabled in simulation mode.
5. Evidence field preservation: `missing_info` in search steps and `category` in source citations are preserved across both backends.
6. Ground-truth benchmark alignment: Benchmark answers are strictly aligned with `src/evaluation/questions.json` (Gloamreach: 246 AS via Codex Vaeloria I, Gauntlet: 391 AS via Codex Vaeloria II).

Reason:
Track 1C judges evaluate how the system visibly reasons across rounds, detects missing information, and searches again. The visual timeline clearly demonstrates the difference between basic 1-shot RAG and Track 1C iterative search. Eliminating silent fallbacks and preventing simulation hallucination guarantees evaluation integrity during judging.

Status:
Accepted
