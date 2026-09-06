"""
Mock search module for Track 1C agent development.

Place this at: src/retrieval/mock_search.py (REPLACES the earlier version --
this file adds the Gloamreach scenario alongside the existing Isolde
Mournvale / Silent Choir scenario. All prior chunks are preserved.)

New in this version
--------------------
Adds a second, harder test scenario based on REAL archive content, for
sample question 1c_000: "State the precise year in the Age of Shadows that
marks the true founding of Gloamreach."

Unlike the Isolde Mournvale scenario (a genuine multi-hop question WITH a
findable answer), this scenario is a deliberate TRAP: the real archive
explicitly states the founding date is contested and unresolved, and even
the document named as the authority (the Annals) does not contain a
resolving year. The correct agent behavior is to report the date as
genuinely disputed/unknown -- NOT to guess or hallucinate a specific year,
even after using all available search rounds.

This tests exactly the checklist items:
  - "Handle conflicting evidence rather than hiding it"
  - "Handle insufficient evidence honestly"
  - Rubric question: "What happens when there is not enough evidence?"

Text below is taken directly (lightly trimmed) from the real archive files:
wiki/gloamreach.md and codex/the_annals_of_the_ashen_era.docx.
"""

from typing import List, Dict

# ---------------------------------------------------------------------------
# Mock chunk data
# ---------------------------------------------------------------------------

MOCK_CHUNKS: List[Dict] = [
    # === Scenario A: Isolde Mournvale / Silent Choir (existing, unchanged) ===
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

    # === Scenario B: Gloamreach founding -- NEW, real "no answer exists" trap ===
    {
        "chunk_id": "wiki_gloamreach_001",
        "text": (
            "Gloamreach is a core location in the Pale Coast region, distinguished "
            "from the surrounding coast by its quarantined status. It is ruled by "
            "House Morvain and maintained with a garrison of 2483. Founded: "
            "Contested; consult the Annals and Codex."
        ),
        "source": "gloamreach.md",
        "page": 1,
        "category": "wiki",
        "score": 0.88,
    },
    {
        "chunk_id": "wiki_gloamreach_002",
        "text": (
            "The recorded history of Gloamreach is inseparable from the uncertainty "
            "surrounding its foundation. Sources contest when the location was "
            "founded, and no founding year is accepted as definitive. Accordingly, "
            "no year should be assigned to its establishment. The Annals and Codex "
            "remain the authorities for examination of the disputed record and "
            "should be consulted in place of later summaries that attempt to settle "
            "the matter without resolving the underlying disagreement."
        ),
        "source": "gloamreach.md",
        "page": 1,
        "category": "wiki",
        "score": 0.93,
    },
    {
        "chunk_id": "codex_annals_gloamreach_001",
        "text": (
            "Annals registry: Isolde Nightbrook, a minor character recorded under "
            "the office of Herbalist, born in 401 AS, member of The Iron-Ring "
            "Cartel, serves at Gloamreach. Annals registry: Maelis Wrenfield, a "
            "Gaoler with duties recorded at Gloamreach, member of The Ashen "
            "Vanguard, born in 393 AS. Annals registry: Brannoc Ironmere the "
            "Red-Handed is assigned Edge of Gloamreach since 314 AS (an office, "
            "not a founding date). No founding year for the location of Gloamreach "
            "itself appears in these registry entries."
        ),
        "source": "the_annals_of_the_ashen_era.docx",
        "page": 1,
        "category": "codex",
        "score": 0.80,
    },
    {
        "chunk_id": "ephemera_petition_gloamreach_001",
        "text": (
            "A petition addressed to the ruling authorities protests the ongoing "
            "quarantine conditions at Gloamreach, describing hardship faced by "
            "residents and requesting relief. The petition makes no reference to "
            "the location's founding or history."
        ),
        "source": "petition_concerning_gloamreach.txt",
        "page": 1,
        "category": "ephemera",
        "score": 0.60,
    },
]


def search(query: str, top_k: int = 15) -> List[Dict]:
    """
    Naive keyword-overlap mock search over MOCK_CHUNKS.
    Returns results sorted by descending score, matching the agreed schema.
    """
    query_terms = set(query.lower().split())
    results = []

    for chunk in MOCK_CHUNKS:
        text_terms = set(chunk["text"].lower().replace(",", "").replace(".", "").split())
        overlap = len(query_terms & text_terms)
        if overlap == 0:
            continue
        adjusted_score = min(0.99, chunk["score"] + 0.01 * overlap)
        results.append({**chunk, "score": round(adjusted_score, 3)})

    results.sort(key=lambda c: c["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    print("=== Scenario A, round 1: Isolde Mournvale ===")
    for r in search("Isolde Mournvale"):
        print(f"  [{r['score']}] {r['source']}: {r['text'][:70]}...")

    print("\n=== Scenario A, round 2: Silent Choir war victory ===")
    for r in search("Silent Choir war victory"):
        print(f"  [{r['score']}] {r['source']}: {r['text'][:70]}...")

    print("\n=== Scenario B, round 1: Gloamreach founding ===")
    for r in search("Gloamreach founding"):
        print(f"  [{r['score']}] {r['source']}: {r['text'][:70]}...")

    print("\n=== Scenario B, round 2: Annals Gloamreach founding year ===")
    for r in search("Annals Gloamreach founding year"):
        print(f"  [{r['score']}] {r['source']}: {r['text'][:70]}...")
