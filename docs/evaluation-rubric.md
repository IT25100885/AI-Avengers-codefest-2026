\# Evaluation Scoring Rules



Use null for anything not yet verified.

Use 0 only when a failure has been confirmed.



| Area | 0 — Failed | 1 — Partial | 2 — Successful |

|---|---|---|---|

| Retrieval | Missed the required evidence | Found some required evidence | Found enough relevant evidence |

| Answer | Incorrect or unsupported | Partly correct or incomplete | Correct and supported by verified evidence |

| Citations | Missing or incorrect | Some claims have valid citations | Key claims have accurate, traceable citations |

| Search behaviour | Failed to follow up when needed, or stopped incorrectly | Follow-up searches made limited progress | Follow-ups addressed missing evidence and stopping was appropriate |



\## Important rules



\- Verify expected answers against the original archive.

\- Do not treat mock-corpus results as full-archive results.

\- More search rounds do not automatically earn a higher score.

\- One round can be sufficient for a direct question.

\- Refusing to answer is correct only when justified by the evidence

&#x20; and the test's verified expected behaviour.

\- Record the reason for each score in reviewer\_notes.



\## Current evaluation status



The evaluator is connected to the agent.

Retrieval still uses src.retrieval.mock\_search.

Full-archive answer accuracy and citation accuracy remain unverified.

