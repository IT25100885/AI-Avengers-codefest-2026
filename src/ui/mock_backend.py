"""
Mock backend module for Track 1C Streamlit UI.

Provides realistic multi-round search responses matching the exact data contract
agreed between Member 2 and Member 3:

{
  "answer": "...",
  "search_steps": [
    {"round": 1, "query": "...", "sources_found": 8, "status": "insufficient"},
    {"round": 2, "query": "...", "sources_found": 5, "status": "sufficient"}
  ],
  "sources": [
    {"source": "codex.pdf", "page": 17}
  ]
}
"""

from typing import Dict, Any, List
import re

MOCK_DATABASE: Dict[str, Dict[str, Any]] = {
    "isolde_war": {
        "pattern": r"(isolde|mournvale|silent choir|war.*won)",
        "answer": (
            "The organization that counted Isolde Mournvale among its members was "
            "**The Silent Choir** (see *isolde_mournvale.md*).\n\n"
            "According to the entry on the conflict, **the War of Drowned Light** is "
            "recorded as an official victory for The Silent Choir (see *the_war_of_drowned_light.md*).\n\n"
            "**Answer:** The Silent Choir won the **War of Drowned Light**.\n\n"
            "*Evidence Trail:* In Round 1, the assistant retrieved Isolde's affiliation with The Silent Choir. "
            "Recognizing that the specific war won was still missing, the assistant generated a second query targeting "
            "The Silent Choir's military record and retrieved the resolving victory."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Isolde Mournvale",
                "sources_found": 2,
                "status": "insufficient",
                "missing_info": "Identified affiliation with The Silent Choir, but specific war victory is not yet retrieved.",
            },
            {
                "round": 2,
                "query": "The Silent Choir war victory",
                "sources_found": 9,
                "status": "sufficient",
                "missing_info": "",
            },
        ],
        "sources": [
            {"source": "isolde_mournvale.md", "page": 1, "category": "wiki"},
            {"source": "the_war_of_drowned_light.md", "page": 1, "category": "wiki"},
            {"source": "the_annals_of_the_ashen_era.docx", "page": 1, "category": "codex"},
        ],
    },
    "gloamreach": {
        "pattern": r"(gloamreach|precise year|founding of gloamreach)",
        "answer": (
            "The sources do not provide a single, definitive year for the founding of Gloamreach. "
            "Both wiki entries explicitly state that the foundation year is **contested** and that no "
            "accepted year exists (*“Founded: Contested; consult the Annals and Codex”*), and the Annals "
            "and Codex themselves contain no entry giving a founding date for the location (the registries list "
            "individuals associated with Gloamreach, but no founding year for the settlement itself).\n\n"
            "**Answer:** A precise year in the Age of Shadows for the true founding of Gloamreach "
            "**cannot be stated** from the available evidence, as the archive explicitly treats the date as disputed.\n\n"
            "*Evidence Trail:* The assistant searched 3 rounds (starting with Gloamreach overview, then attempting specific "
            "date queries). Rather than hallucinating a year, it honestly reported the historical conflict."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Gloamreach",
                "sources_found": 4,
                "status": "insufficient",
                "missing_info": "Settlement overview found, but founding date is marked as 'Contested; consult the Annals'.",
            },
            {
                "round": 2,
                "query": "Gloamreach founding year Age of Shadows precise date",
                "sources_found": 9,
                "status": "insufficient",
                "missing_info": "Codex records individuals stationed at Gloamreach, but no settlement founding year exists.",
            },
            {
                "round": 3,
                "query": "Gloamreach established Year of the Black Dawn Age of Shadows record",
                "sources_found": 9,
                "status": "insufficient",
                "missing_info": "Max rounds reached. Date is genuinely contested across authoritative archives.",
            },
        ],
        "sources": [
            {"source": "gloamreach.md", "page": 1, "category": "wiki"},
            {"source": "the_annals_of_the_ashen_era.docx", "page": 1, "category": "codex"},
            {"source": "petition_concerning_gloamreach.txt", "page": 1, "category": "ephemera"},
        ],
    },
    "gauntlet": {
        "pattern": r"(gauntlet|sorrowfell)",
        "answer": (
            "The archive contains no record of an item called the **“Gauntlet of Sorrowfell,”** "
            "nor any date for its forging. None of the wiki entries, codex armories, or ephemera "
            "in the current archive index mention this artifact.\n\n"
            "**Answer:** The forging year cannot be determined because the Gauntlet of Sorrowfell "
            "is unrecorded in the available archive materials.\n\n"
            "*Evidence Trail:* The assistant performed 3 rounds of targeted searches across multiple keyword variations. "
            "Having found no positive match, it accurately reported the absence of evidence."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Gauntlet of Sorrowfell",
                "sources_found": 0,
                "status": "insufficient",
                "missing_info": "No direct matches for the artifact name.",
            },
            {
                "round": 2,
                "query": "Gauntlet of Sorrowfell forged year",
                "sources_found": 0,
                "status": "insufficient",
                "missing_info": "No relics or armory records matching Sorrowfell forging.",
            },
            {
                "round": 3,
                "query": "Gauntlet of Sorrowfell forging date",
                "sources_found": 0,
                "status": "insufficient",
                "missing_info": "No supporting evidence found after 3 rounds.",
            },
        ],
        "sources": [
            {"source": "the_annals_of_the_ashen_era.docx", "page": 1, "category": "codex"},
        ],
    },
    "direct_membership": {
        "pattern": r"(which organization includes isolde|isolde.*member)",
        "answer": (
            "Isolde Mournvale is recorded as a member of **The Silent Choir** (*isolde_mournvale.md*).\n\n"
            "**Answer:** The Silent Choir.\n\n"
            "*Evidence Trail:* This direct single-hop question was satisfied immediately in Round 1."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Isolde Mournvale",
                "sources_found": 2,
                "status": "sufficient",
                "missing_info": "",
            },
        ],
        "sources": [
            {"source": "isolde_mournvale.md", "page": 1, "category": "wiki"},
            {"source": "the_annals_of_the_ashen_era.docx", "page": 1, "category": "codex"},
        ],
    },
    "nonsense": {
        "pattern": r"(asdfgh|qwerty|zxcvbn)",
        "answer": (
            "The input cannot be interpreted as a meaningful query regarding the Ashen Era Archive. "
            "No historical entities, artifacts, or events could be extracted. "
            "Please provide a coherent question regarding the archive."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "asdfgh qwerty zxcvbn",
                "sources_found": 0,
                "status": "insufficient",
                "missing_info": "Input does not map to any recognized historical term.",
            },
        ],
        "sources": [],
    },
}


def mock_answer_question(question: str) -> Dict[str, Any]:
    """
    Produce a deterministic mock answer matching the team's agreed schema:
    {
      "answer": "...",
      "search_steps": [
        {"round": 1, "query": "...", "sources_found": 8, "status": "insufficient"},
        {"round": 2, "query": "...", "sources_found": 5, "status": "sufficient"}
      ],
      "sources": [
        {"source": "codex.pdf", "page": 17}
      ]
    }
    """
    q_clean = question.strip().lower()

    if not q_clean:
        return {
            "answer": "No question was provided. Please enter an inquiry to search the archive.",
            "search_steps": [],
            "sources": [],
        }

    # Match known scenario
    for scenario_key, scenario in MOCK_DATABASE.items():
        if re.search(scenario["pattern"], q_clean):
            # Format clean sources for the contract
            clean_sources = [
                {"source": s["source"], "page": s.get("page")}
                for s in scenario["sources"]
            ]
            clean_steps = [
                {
                    "round": s["round"],
                    "query": s["query"],
                    "sources_found": s["sources_found"],
                    "status": s["status"],
                }
                for s in scenario["search_steps"]
            ]
            return {
                "answer": scenario["answer"],
                "search_steps": clean_steps,
                "sources": clean_sources,
            }

    # Generic fallback for freeform queries
    first_query = question.strip().split("?")[0]
    words = [w for w in first_query.split() if len(w) > 3]
    entity = " ".join(words[:2]) if words else "Archive Subject"

    return {
        "answer": (
            f"Based on analysis of the Ashen Era Archive, the evidence regarding **{question.strip()}** "
            "was synthesized across multiple documents. Key historical records confirm the primary relationship "
            "established during the Age of Shadows.\n\n"
            f"**Synthesized Answer:** Evidence points to recorded accounts in the regional codex and chronicles."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": entity,
                "sources_found": 3,
                "status": "insufficient",
            },
            {
                "round": 2,
                "query": f"{entity} historical record Ashen Era",
                "sources_found": 5,
                "status": "sufficient",
            },
        ],
        "sources": [
            {"source": "codex_vaeloria_i_gazetteer_of_the_sundered_realms.pdf", "page": 14},
            {"source": "the_annals_of_the_ashen_era.docx", "page": 1},
        ],
    }
