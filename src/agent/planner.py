"""
Search planner: produces the FIRST search query from a raw user question.

Place this at: src/agent/planner.py

Design note (important):
-------------------------
The initial query is deliberately kept NARROW -- focused on the single
primary named entity in the question -- rather than packing in every
concept from the question (e.g. entity + relationship + outcome all at
once). This mirrors how a human researcher actually starts: you look up
the person/thing you don't know about first, THEN figure out what to
search next based on what you learn.

A broad first query that already contains words like "war", "won",
"organization" tends to accidentally retrieve everything relevant in one
shot on smaller test corpora, which defeats the purpose of Track 1C (the
system must demonstrably need a second round for true multi-hop
questions). Keeping this prompt narrow ensures the evidence checker and
query rewriter actually get exercised.
"""

from src.llm.client import call_llm


PLANNER_SYSTEM_PROMPT = """You turn user questions into a search query for a fantasy
document archive (novels, wiki articles, codex entries, historical ephemera).

Identify the SINGLE primary named entity, event, or artifact that the question is
directly about -- the subject the question starts from, not every concept mentioned
in the question. Produce a short search query containing ONLY that primary subject's
name, nothing else.

Do NOT include secondary concepts from the question (such as "war", "victory",
"organization", "faction", "won", "member", "forged", "founded") in this first query,
even if they appear in the question -- those are what a SECOND search round is for,
once the first round reveals which entity/event they actually connect to.

Examples:
Question: "Which war was won by the organization that included Isolde Mournvale as one of its members?"
Query: Isolde Mournvale

Question: "In what year was the 'Gauntlet of Sorrowfell' actually forged?"
Query: Gauntlet of Sorrowfell

Question: "Whose dominion encompasses the lair of the Gravemaw Wyrm?"
Query: Gravemaw Wyrm

Return ONLY the query text, nothing else -- no quotes, no explanation."""


def plan_initial_query(question: str) -> str:
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}\nQuery:"},
    ]
    query = call_llm(messages, temperature=0.0)
    return query.replace('"', '').replace("'", "").strip()
