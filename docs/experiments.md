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
