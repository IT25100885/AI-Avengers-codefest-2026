"""
Evidence sufficiency checker for the Track 1C iterative search loop.

Place this at: src/agent/evidence_checker.py
"""
from src.llm.client import call_llm_json


SUFFICIENCY_SYSTEM_PROMPT = """You are a strict evidence-sufficiency judge for a research assistant.

You will be given a QUESTION and a list of EVIDENCE snippets retrieved so far.
Decide whether the evidence, taken together, contains enough concrete facts to
fully and correctly answer the question -- without guessing or filling gaps
with outside knowledge.

Rules:
- If the evidence only gives you a PART of a multi-step fact chain (e.g. it names
  a person's affiliation but not the outcome tied to that affiliation, or names an
  event but not the specific detail asked about), mark it INSUFFICIENT and say
  exactly what is missing.
- If multiple pieces of evidence conflict, still mark it SUFFICIENT if you can
  identify which source is more authoritative (e.g. an official codex/wiki entry
  over a ballad/folklore), but flag the conflict in your reasoning.
- Do not mark something sufficient just because a lot of evidence was retrieved --
  judge based on whether the SPECIFIC question is answerable.

Respond with ONLY a JSON object in this exact shape:
{
  "status": "sufficient" | "insufficient",
  "missing_information": "<specific description of what's missing, or empty string if sufficient>",
  "reasoning": "<one or two sentences explaining the judgment>"
}
"""


def check_sufficiency(question: str, evidence: list[dict]) -> dict:
    evidence_text = "\n\n".join(
        f"[{i+1}] (source: {e['source']}, category: {e.get('category', 'unknown')})\n{e['text']}"
        for i, e in enumerate(evidence)
    )
    messages = [
        {"role": "system", "content": SUFFICIENCY_SYSTEM_PROMPT},
        {"role": "user", "content": f"QUESTION: {question}\n\nEVIDENCE:\n{evidence_text}"},
    ]
    result = call_llm_json(messages, temperature=0.0)

    # Defensive defaults in case the model returns non-dict or omits a key
    if not isinstance(result, dict):
        result = {"status": "insufficient", "missing_information": "", "reasoning": str(result)}

    result.setdefault("status", "insufficient")
    result.setdefault("missing_information", "")
    result.setdefault("reasoning", "")
    return result
