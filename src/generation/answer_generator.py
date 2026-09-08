"""
Final answer generator: synthesizes a grounded answer from accumulated evidence.

Place this at: src/generation/answer_generator.py
"""
from src.llm.client import call_llm


GENERATOR_SYSTEM_PROMPT = """You answer questions using ONLY the evidence provided.
Do not use outside knowledge. If the provided evidence does not contain facts
directly relevant to the question, state clearly and honestly that no relevant
evidence was found in the archive, rather than speculating or using unrelated context.
If sources conflict, prefer official/canonical sources (wiki, codex) over informal
ones (ballads, folklore, rumor) and briefly note the conflict. If the evidence
genuinely does not support a confident answer, say so honestly instead of guessing.
Cite which source(s) your answer relies on."""


def generate_answer(question: str, evidence: list[dict]) -> str:
    if not evidence:
        return "No relevant information was found in the Ashen Era Archive to answer this question."

    evidence_text = "\n\n".join(
        f"[Source: {e['source']}, category: {e.get('category', 'unknown')}]\n{e['text']}"
        for e in evidence
    )
    messages = [
        {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"QUESTION: {question}\n\nEVIDENCE:\n{evidence_text}\n\nANSWER:"},
    ]
    return call_llm(messages, temperature=0.1).strip()
