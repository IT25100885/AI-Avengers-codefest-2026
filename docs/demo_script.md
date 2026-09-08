# SLIIT Codefest 2026 - Track 1C Live Demo Script (3-4 Minutes)

**Role**: Member 3 (Streamlit UI & Application Integration Engineer)  
**System**: Ashen Era Agentic Search Assistant  
**Sub-Track**: 1C — Searching the Way a Human Does  

---

## Demo Goals for Judges
1. Prove that the assistant is **not basic 1-shot RAG**, but an **autonomous iterative researcher**.
2. Visibly showcase multi-round search, query reformulation, and evidence sufficiency evaluation.
3. Demonstrate that the system **consults authoritative codices to resolve contested dates** (Gloamreach 246 AS, Gauntlet 391 AS).
4. Highlight adherence to the agreed competition data contract (`answer`, `search_steps`, `sources`).
5. Demonstrate parameter control (`max_rounds`, `top_k`) in live reasoning mode.

---

## 3-4 Minute Presentation Timeline

### 0:00 – 0:45 | Introduction & Problem Setup
- **Action**: Open the UI at `http://localhost:8501`.
- **Spoken Script**:
  > *"Judges, welcome. We are team AI Avengers representing Sub-track 1C: 'Searching the Way a Human Does'. In traditional RAG, a chatbot runs a single embedding search and attempts to answer in one shot. In the Ashen Era Archive, questions are often complex and multi-hop. A human researcher searches, inspects the evidence, notices when initial wiki summaries are incomplete or contested, reformulates the search query to consult authoritative codices, and repeats until they have a grounded answer. That is exactly what our Streamlit system demonstrates today."*

---

### 0:45 – 1:35 | Demo 1: True Multi-Hop Search (Question 1b_005)
- **Action**: Under **"Choose a competition benchmark question"**, select:
  `🔥 [1b_005 Multi-Hop] Which war was won by the organization that included Isolde Mournvale as one of its members?`
  Click **🔍 Search Archive**.
- **What is on screen**:
  - **Round 1**:
    - Query: `Isolde Mournvale`
    - Status: `⚠️ Insufficient Evidence (Searching Again)`
    - Decision Trail: Assistant extracted the primary entity, retrieved her membership in **The Silent Choir**, recognized that the war won is not yet found, and paused to reformulate.
  - **Round 2**:
    - Query: `The Silent Choir war victory`
    - Status: `✅ Sufficient Evidence`
    - Found conflict resolution: **The War of Drowned Light**.
  - **Grounded Answer**:
    - Clearly states the Silent Choir won the War of Drowned Light with cited sources (`isolde_mournvale.md`, `the_war_of_drowned_light.md`).
- **Spoken Script**:
  > *"Notice what happened here: In Round 1, the agent retrieved Isolde's affiliation with The Silent Choir. The evidence checker flagged this as insufficient because the war victory was still missing. The rewriter generated a targeted second query for 'The Silent Choir war victory', which concluded in Round 2 with full citations."*

---

### 1:35 – 2:30 | Demo 2: Resolving Contested Evidence via Authoritative Codex (Question 1c_000)
- **Action**: Select preset:
  `🏛️ [1c_000 Multi-Round Benchmark] State the precise year in the Age of Shadows that marks the true founding of Gloamreach.`
  Click **🔍 Search Archive**.
- **What is on screen**:
  - **Round 1**: Query `Gloamreach` &rarr; wiki records that founding is contested and directs consultation of the Codex. Status: `⚠️ Insufficient Evidence`.
  - **Round 2**: Query `Codex Vaeloria Gloamreach founding year Age of Shadows` &rarr; consults **Codex Vaeloria I: Gazetteer of the Sundered Realms** (page 23).
  - **Status**: `✅ Sufficient Evidence`.
  - **Final Answer**:
    - Concludes that Gloamreach was founded in **246 AS**, noting that the authoritative Codex explicitly rejects competing popular claims.
- **Spoken Script**:
  > *"In Question 1c_000, the initial wiki article marks the founding year as contested. Instead of hallucinating or giving up, the assistant follows the wiki's reference to the authoritative Codex Vaeloria I, performing a second targeted search that confirms the true founding year: 246 AS."*

---

### 2:30 – 3:00 | Demo 3: Direct Lookup & Unsupported Query Boundaries
- **Action**:
  1. Select preset `🎯 [Direct Lookup] Which organization includes Isolde Mournvale as a member?`.
     Show that it completes immediately in **Round 1** (`The Silent Choir`), without needlessly executing a second war search.
  2. Enter a custom unsupported query in simulation mode.
     Show that it cleanly displays: *"No simulation available for this question"*, proving the simulation does not invent fake facts or fabricated search steps.
- **Spoken Script**:
  > *"Notice our boundaries: direct single-hop questions resolve in 1 round without unnecessary looping, and our simulation mode refuses to invent fake answers for unsupported questions, preserving complete integrity."*

---

### 3:00 – 3:30 | Demo 4: Live Agent Architecture & Parameter Control
- **Action**:
  - In the sidebar, toggle to **Live Agent Pipeline (`src.agent.search_agent`)**.
  - Highlight the active **Max Search Rounds** and **Retrieval Top-K** sliders.
  - Scroll to the bottom and expand **"🔍 Inspect Official Data Contract JSON"**.
- **Spoken Script**:
  > *"In Live Agent Mode, our sliders dynamically pass search budgets into the reasoning loop. If an API key is missing or fails, the interface displays the error transparently without silent fallbacks. And as you can see in the JSON inspector, our schema strictly complies with the competition contract."*

---

### 3:30 – 4:00 | Summary & Q&A Handoff
- **Spoken Script**:
  > *"In summary, Member 3's UI provides a transparent, demo-ready window into the assistant's decision-making process. Thank you, and we welcome your questions!"*

---

## Anticipated Judge Q&A Cheat Sheet

1. **Q: What makes your solution Track 1C rather than normal RAG?**  
   *A: Normal RAG does `query -> 1 retrieval -> LLM answer`. Track 1C uses an autonomous loop: `query -> retrieval -> sufficiency check -> gap detection -> query rewrite -> repeat until grounded`.*

2. **Q: Why are Gloamreach and Gauntlet dates 246 AS and 391 AS?**  
   *A: As verified in `src/evaluation/questions.json`, Codex Vaeloria I (p. 23) establishes Gloamreach was founded in 246 AS, and Codex Vaeloria II (p. 11) confirms the Gauntlet was forged in 391 AS. Both codices explicitly reject contrary popular accounts.*

3. **Q: What is the current retrieval status of Live Agent Mode?**  
   *A: Live Agent Mode runs the real Groq LLM reasoning agent (`src.agent.search_agent`) over structured archive retrieval (`src.retrieval.mock_search`). Member 1's ChromaDB and Voyage embedding pipeline over the full corpus will plug in seamlessly to replace the mock retrieval backend.*

4. **Q: How can a judge run this from a clean machine?**  
   *A: Clone the repository, run `pip install -r requirements.txt`, and execute `streamlit run src/app.py`. Simulation mode runs instantly out-of-the-box without needing external API keys.*
