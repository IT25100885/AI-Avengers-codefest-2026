## LLM model selection (Groq) — [today's date] — Abdullah

Initially configured for `llama-3.3-70b-versatile`, which returned a 404
(model no longer available on our account). Queried Groq's /v1/models
endpoint directly to get the real list of accessible models, and switched
to `openai/gpt-oss-120b` for stronger multi-hop reasoning and reliable
structured JSON output, needed for the evidence-sufficiency checker.
Verified with both a plain text call and a structured JSON call before
proceeding.
