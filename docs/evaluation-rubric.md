# Evaluation Scoring Rules

Use `null` for anything that has not yet been verified.

Use `0` only when a failure has actually been confirmed.

## Scoring Scale

| Area | 0 — Failed | 1 — Partial | 2 — Successful |
|---|---|---|---|
| Retrieval | Required evidence was not retrieved | Some relevant evidence was retrieved | Enough relevant evidence was retrieved |
| Answer | Incorrect, unsupported, or missing | Partly correct or incomplete | Correct and supported by verified evidence |
| Citations | Missing or incorrect | Some citations are valid | Key claims have accurate, traceable citations |
| Search Behaviour | Did not search again when needed, repeated useless searches, or stopped incorrectly | Follow-up searches made limited progress | Follow-up searches targeted missing information and stopped appropriately |

## Failure Reason Categories

When a question fails, use one of the following values for `failure_reason`:

- `extraction` — required information was not extracted from the document.
- `retrieval` — the required evidence existed but was not retrieved.
- `reranking` — relevant evidence was retrieved but ranked too low or excluded.
- `query_rewrite` — the follow-up query did not properly target the missing information.
- `llm_reasoning` — sufficient evidence was available but the reasoning or answer was wrong.
- `citation` — the answer was correct but the citation/source information was wrong or missing.
- `input_handling` — invalid or unclear input was handled incorrectly.
- `no_failure` — the test completed successfully.
- `unknown` — the failure has not yet been diagnosed.

## Important Rules

- Verify expected answers against the original Ashen Era Archive.
- Do not treat mock-retrieval results as full-archive retrieval results.
- More search rounds do not automatically mean a better result.
- A direct lookup question may correctly finish after one round.
- A multi-step question should continue searching when important evidence is still missing.
- Refusing to answer is correct only when the archive genuinely does not provide enough evidence.
- Record a short explanation for each score in `reviewer_notes`.
- Do not give final retrieval or citation scores until real full-archive retrieval is integrated.

## Current Evaluation Status

The evaluation harness is connected to the real reasoning agent.

The reasoning agent currently still uses:

```python
from src.retrieval.mock_search import search