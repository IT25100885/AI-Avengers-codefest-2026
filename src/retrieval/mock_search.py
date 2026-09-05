"""
Mock search module for Track 1C agent development.

Purpose
-------
Member 1's real search() is not ready yet. This module provides a fake but
REALISTIC search() that returns data in the exact schema the team agreed on,
built from real facts in the actual Ashen Era Archive (wiki/the_war_of_drowned_light.md,
wiki/the_silent_choir.md, wiki/isolde_mournvale.md).

Interface contract (must match Member 1's eventual real search()):
    search(query: str, top_k: int = 15) -> list[dict]
    each dict: {chunk_id, text, source, page, category, score}

Why this specific scenario
---------------------------
This mock reproduces sample question 1b_005:
    "Which war was won by the organization that included Isolde Mournvale
     as one of its members?"

This is a genuine 2-hop question. No single chunk below answers it directly:
  - Chunk A says Isolde Mournvale is a member of The Silent Choir.
  - Chunk B says The Silent Choir won the War of Drowned Light.
A correct agent must search once, realize it only has half the answer,
reformulate its query around "The Silent Choir", search again, and only
then produce a grounded final answer.

Swap-out plan: once Member 1's real search() is ready, replace the import
`from mock_search import search` with `from src.retrieval.search import search`.
No other code should need to change if the interface is respected.
"""

from typing import List, Dict

# ---------------------------------------------------------------------------
# Mock chunk data (grounded in the real archive's wiki articles)
# ---------------------------------------------------------------------------

MOCK_CHUNKS: List[Dict] = [
    # --- Round 1 bait: mentions Isolde Mournvale, gives her faction, NOT the war ---
    {
        "chunk_id": "wiki_isolde_mournvale_001",
        "text": (
            "Isolde Mournvale is a minor figure of the Ashen Era, born in 341 AS. "
            "She serves as a falconer and is a member of The Silent Choir. "
            "Her known service is located at Stormmarch."
        ),
        "source": "isolde_mournvale.md",
        "page": 1,
        "category": "wiki",
        "score": 0.90,
    },
    # --- Round 1 bait: general Silent Choir background, no war outcome ---
    {
        "chunk_id": "wiki_silent_choir_001",
        "text": (
            "The Silent Choir is a secretive priesthood that records, censors, and "
            "rewrites history. It is seated at Vharencrag Fortress and has been "
            "belligerent in The War of Drowned Light, The War of Endless Vigil, "
            "and The Winter Reckoning."
        ),
        "source": "the_silent_choir.md",
        "page": 1,
        "category": "wiki",
        "score": 0.83,
    },
    # --- Round 2 payoff: only surfaces well on a query naming "Silent Choir" + "war"/"victor" ---
    {
        "chunk_id": "wiki_war_drowned_light_001",
        "text": (
            "The War of Drowned Light began in 225 AS and ended in 235 AS, producing "
            "64617 casualties. Although the conflict is recorded as a victory for "
            "The Silent Choir, its origin remained obscured: the spark that started "
            "the war was secretly staged by The Silent Choir."
        ),
        "source": "the_war_of_drowned_light.md",
        "page": 1,
        "category": "wiki",
        "score": 0.95,
    },
    # --- Distractor: a different war, different faction, to test the agent doesn't conflate wars ---
    {
        "chunk_id": "wiki_winter_reckoning_001",
        "text": (
            "The Winter Reckoning was a conflict fought primarily in the northern "
            "reaches. The Silent Choir participated as a belligerent, but the "
            "recorded victor of this conflict was House Morvain, not The Silent Choir."
        ),
        "source": "the_winter_reckoning.md",
        "page": 1,
        "category": "wiki",
        "score": 0.71,
    },
    # --- Distractor: unreliable/conflicting source, for later conflict-handling tests ---
    {
        "chunk_id": "ephemera_ballad_vharenford_001",
        "text": (
            "A tavern ballad claims the War of Drowned Light was truly won by "
            "wandering mercenaries, not The Silent Choir -- most scholars dismiss "
            "this as folklore invented long after the war's end."
        ),
        "source": "ballad_concerning_vharenford.txt",
        "page": 1,
        "category": "ephemera",
        "score": 0.55,
    },
]


def search(query: str, top_k: int = 15) -> List[Dict]:
    """
    Naive keyword-overlap mock search over MOCK_CHUNKS.

    This intentionally behaves like a rough retrieval system: a query about
    "Isolde Mournvale" surfaces her bio chunk (which reveals her faction) but
    NOT the war-outcome chunk. Only a follow-up query that mentions
    "Silent Choir" together with war/victor-related terms will rank the
    war-outcome chunk highly enough to matter.

    Returns results sorted by descending score, matching the agreed schema.
    """
    query_terms = set(query.lower().split())
    results = []

    for chunk in MOCK_CHUNKS:
        text_terms = set(chunk["text"].lower().replace(",", "").replace(".", "").split())
        overlap = len(query_terms & text_terms)
        if overlap == 0:
            continue
        # Boost score slightly based on overlap, capped at 0.99
        adjusted_score = min(0.99, chunk["score"] + 0.01 * overlap)
        results.append({**chunk, "score": round(adjusted_score, 3)})

    results.sort(key=lambda c: c["score"], reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# Quick manual test (run this file directly to sanity-check behavior)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Round 1 query: about Isolde Mournvale ===")
    round1 = search("Isolde Mournvale faction member")
    for r in round1:
        print(f"  [{r['score']}] {r['source']}: {r['text'][:80]}...")

    print("\n=== Round 2 query: about Silent Choir war victory ===")
    round2 = search("Silent Choir war victor won")
    for r in round2:
        print(f"  [{r['score']}] {r['source']}: {r['text'][:80]}...")
