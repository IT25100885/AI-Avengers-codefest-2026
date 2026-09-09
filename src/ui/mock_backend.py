"""
Mock backend module for Track 1C Streamlit UI.

Provides deterministic multi-round search responses matching the exact data contract
agreed between Member 2 and Member 3 for pre-configured competition benchmark questions:

{
  "answer": "...",
  "search_steps": [
    {"round": 1, "query": "...", "sources_found": 8, "status": "insufficient", "missing_info": "..."},
    {"round": 2, "query": "...", "sources_found": 5, "status": "sufficient", "missing_info": "..."}
  ],
  "sources": [
    {"source": "codex.pdf", "page": 17, "category": "codex"}
  ]
}
"""

from typing import Dict, Any, List
import re

SIMULATION_BANNER = "[DEMONSTRATION / SIMULATION MODE: Pre-computed benchmark trace]\n\n"


def normalize_query(text: str) -> str:
    """Normalize query text for exact benchmark matching."""
    t = text.lower().strip()
    t = re.sub(r'["\'\?\.\,\!\;\:\`\(\)\[\]]', '', t)
    return " ".join(t.split())


BENCHMARK_PRESETS: Dict[str, Dict[str, Any]] = {
    # 1. Multi-Hop Investigation (1b_005)
    "1b_005": {
        "canonical_question": "Which war was won by the organization that included Isolde Mournvale as one of its members?",
        "normalized_matches": {
            "which war was won by the organization that included isolde mournvale as one of its members",
        },
        "answer": (
            SIMULATION_BANNER +
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

    # 2. Direct Lookup (internal_direct_001)
    "internal_direct_001": {
        "canonical_question": "Which organization includes Isolde Mournvale as a member?",
        "normalized_matches": {
            "which organization includes isolde mournvale as a member",
        },
        "answer": (
            SIMULATION_BANNER +
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

    # 3. Gloamreach Founding Year (1c_000: Corrected ground truth 246 AS)
    "1c_000": {
        "canonical_question": "State the precise year in the Age of Shadows that marks the true founding of Gloamreach.",
        "normalized_matches": {
            "state the precise year in the age of shadows that marks the true founding of gloamreach",
        },
        "answer": (
            SIMULATION_BANNER +
            "According to **Codex Vaeloria I: Gazetteer of the Sundered Realms** (page 23), "
            "the true founding of Gloamreach occurred in **246 AS** during the Age of Shadows.\n\n"
            "While popular accounts and general wiki entries note the foundation year as contested, "
            "the primary codex explicitly rejects contrary popular accounts and establishes **246 AS** "
            "as the authoritative founding date.\n\n"
            "**Answer:** 246 AS.\n\n"
            "*Evidence Trail:* In Round 1, initial wiki retrieval flagged the founding year as disputed and directed "
            "consultation of the authoritative codex. In Round 2, the assistant targeted Codex Vaeloria I and retrieved "
            "the definitive resolution."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Gloamreach",
                "sources_found": 4,
                "status": "insufficient",
                "missing_info": "Settlement overview found, but founding date is marked contested; directs consultation of Codex Vaeloria I.",
            },
            {
                "round": 2,
                "query": "Codex Vaeloria Gloamreach founding year Age of Shadows",
                "sources_found": 3,
                "status": "sufficient",
                "missing_info": "",
            },
        ],
        "sources": [
            {"source": "codex/codex_vaeloria_i_gazetteer_of_the_sundered_realms.pdf", "page": 23, "category": "codex"},
            {"source": "gloamreach.md", "page": 1, "category": "wiki"},
        ],
    },

    # 4. Gauntlet of Sorrowfell Forging Year (1c_003: Corrected ground truth 391 AS)
    "1c_003": {
        "canonical_question": "In which year was the 'Gauntlet of Sorrowfell' actually forged?",
        "normalized_matches": {
            "in which year was the gauntlet of sorrowfell actually forged",
        },
        "answer": (
            SIMULATION_BANNER +
            "The **Gauntlet of Sorrowfell** was forged in **391 AS**.\n\n"
            "Authoritative records in **Codex Vaeloria II: Armory of Relics and Bestiary** (page 11) "
            "confirm this date in the Gauntlet of Sorrowfell entry and explicitly reject competing dates.\n\n"
            "**Answer:** 391 AS.\n\n"
            "*Evidence Trail:* In Round 1, general armory search was insufficient for exact forging year. "
            "In Round 2, the assistant searched Codex Vaeloria II and retrieved the verified year 391 AS."
        ),
        "search_steps": [
            {
                "round": 1,
                "query": "Gauntlet of Sorrowfell",
                "sources_found": 1,
                "status": "insufficient",
                "missing_info": "Artifact identified, but verified forging date requires consultation of Codex Vaeloria II armory.",
            },
            {
                "round": 2,
                "query": "Codex Vaeloria II Gauntlet of Sorrowfell forged year",
                "sources_found": 2,
                "status": "sufficient",
                "missing_info": "",
            },
        ],
        "sources": [
            {"source": "codex/codex_vaeloria_ii_armory_of_relics_and_bestiary.pdf", "page": 11, "category": "codex"},
        ],
    },

    # 5. Robustness / Nonsense Input (internal_nonsense_001)
    "internal_nonsense_001": {
        "canonical_question": "asdfgh qwerty zxcvbn ???",
        "normalized_matches": {
            "asdfgh qwerty zxcvbn",
        },
        "answer": (
            SIMULATION_BANNER +
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
                "missing_info": "Input does not map to any recognized historical term in the archive.",
            },
        ],
        "sources": [],
    },
}

# Backward compatibility map
MOCK_DATABASE = BENCHMARK_PRESETS


def mock_answer_question(question: str) -> Dict[str, Any]:
    """
    Produce a deterministic mock answer matching the team's agreed schema.
    Strictly matches exact normalized preset questions or explicit preset IDs;
    rejects any other questions cleanly without inventing answers.
    """
    if not question or not question.strip():
        return {
            "answer": "No question was provided. Please enter an inquiry to search the archive.",
            "search_steps": [],
            "sources": [],
            "is_unsupported": False,
        }

    norm_q = normalize_query(question)
    raw_clean = question.strip().lower()

    # Match by explicit preset ID or exact normalized benchmark question
    matched_scenario = None
    for preset_id, scenario in BENCHMARK_PRESETS.items():
        if raw_clean == preset_id.lower():
            matched_scenario = scenario
            break
        for target in scenario["normalized_matches"]:
            if norm_q == normalize_query(target) or raw_clean == target.lower():
                matched_scenario = scenario
                break
        if matched_scenario:
            break

    if matched_scenario:
        clean_sources = [
            {
                "source": s["source"],
                "page": s.get("page"),
                "category": s.get("category", "archive"),
            }
            for s in matched_scenario["sources"]
        ]
        clean_steps = [
            {
                "round": s["round"],
                "query": s["query"],
                "sources_found": s["sources_found"],
                "status": s["status"],
                "missing_info": s.get("missing_info", ""),
            }
            for s in matched_scenario["search_steps"]
        ]
        return {
            "answer": matched_scenario["answer"],
            "search_steps": clean_steps,
            "sources": clean_sources,
            "is_unsupported": False,
        }

    # Strict rejection of unsupported questions in simulation mode
    return {
        "answer": (
            "No simulation available for this question. Simulation mode only supports pre-configured "
            "benchmark questions. To search the archive for arbitrary questions, please switch to "
            "Live Agent Pipeline in the sidebar."
        ),
        "search_steps": [],
        "sources": [],
        "is_unsupported": True,
    }
