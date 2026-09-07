# Experiments

## Experiment 001: Initial mock evaluation

Date: 2026-09-04

Goal:
Verify that the evaluation runner can load questions and save results.

Configuration:
- Backend: Mock answer_question()
- Questions tested: 1
- Search rounds: 2

Results:
- Evaluation file created successfully
- Search steps were recorded
- Sources were recorded

Conclusion:
The evaluation framework is ready to connect to the real backend.

## Experiment 002: Insufficient-evidence handling (Gloamreach trap question)

Date: 2026-09-06

Goal:
Verify that the agent correctly handles genuine "no answer exists / contested source" questions without hallucinating.

Configuration:
- Question tested: Sample question 1c_000 ("true founding year of Gloamreach")
- Corpus: Mock corpus built from real archive files where the founding date is explicitly recorded as disputed/unresolved
- Max search rounds: 3

Results:
- The agent ran all 3 search rounds.
- Never falsely declared sufficiency.
- Produced an honest final answer explaining the dispute with citations rather than hallucinating a specific year.

Conclusion:
Confirms the evidence-checker and answer-generator correctly handle genuine "no answer exists" cases, not just answerable multi-hop questions.

## Experiment 003: Query sanitization verification
Date: 2026-09-06

Goal:
Confirm control-character stripping fix resolves malformed queries
observed in earlier evaluation runs (e.g. trailing null byte in a
query_rewriter output).

Configuration:
- Same 2-question evaluation set (1c_000, 1c_003)
- Re-ran after adding regex-based control-character stripping to
  planner.py and query_rewriter.py

Results:
- All search_steps queries across both questions, all 3 rounds, are now
  free of stray quotes and control characters.
- Both questions still produce correct, honest final answers
  (disputed/unknown, no hallucination).

Conclusion:
Fix verified with no regressions to answer quality or search behavior.
