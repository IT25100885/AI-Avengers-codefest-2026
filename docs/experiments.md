# Experiments Log

## Experiment: insufficient-evidence handling (Gloamreach trap question)
Tested sample question 1c_000 ("true founding year of Gloamreach") against
a mock corpus built from the real archive, where the source material
explicitly states the founding date is disputed/unresolved. Result: the
agent correctly ran all 3 search rounds, never falsely declared
sufficiency, and produced an honest final answer explaining the dispute
with citations -- rather than hallucinating a specific year. This confirms
the evidence-checker and answer-generator correctly handle genuine
"no answer exists" cases, not just answerable multi-hop questions.
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
