# SLIIT Codefest 2026 - Track 1C Live Demo Script (3-4 Minutes)

**Role**: Member 3 (Streamlit UI & Application Integration Engineer)  
**System**: Ashen Era Agentic Search Assistant  
**Sub-Track**: 1C — Searching the Way a Human Does  

---

## Demo Goals for Judges
1. Prove that the assistant is **not basic 1-shot RAG**, but an **autonomous iterative researcher**.
2. Visibly showcase multi-round search, query reformulation, and evidence sufficiency evaluation.
3. Demonstrate that the system **honestly reports contested dates and missing evidence** instead of hallucinating.
4. Highlight adherence to the agreed competition data contract (`answer`, `search_steps`, `sources`).

---

## 3-4 Minute Presentation Timeline

### 0:00 – 0:45 | Introduction & Problem Setup
- **Action**: Open the UI at `http://localhost:8501`.
- **Spoken Script**:
  > *"Judges, welcome. We are team AI Avengers representing Sub-track 1C: 'Searching the Way a Human Does'. In traditional RAG, a chatbot runs a single embedding search and attempts to answer in one shot. In the Ashen Era Archive, questions are often complex, multi-hop, or deliberately contested. A human researcher searches, inspects the evidence, identifies what's missing, reformulates the search query, and repeats until they have a grounded answer. That is exactly what our Streamlit system demonstrates today."*

---

### 0:45 – 1:45 | Demo 1: True Multi-Hop Search (Question 1b_005)
- **Action**: Under **"Choose a competition benchmark question"**, select:
  `🔥 [1b_005 Multi-Hop] Which war was won by the organization that included Isolde Mournvale as one of its members?`
  Click **🔍 Search Archive**.
- **What is on screen**:
  - **Round 1**:
    - Query: `Isolde Mournvale`
    - Status: `⚠️ Insufficient Evidence (Searching Again)`
    - Explanation: Assistant extracted the primary entity, retrieved her membership in **The Silent Choir**, recognized that the war won is not yet found, and paused to reformulate.
  - **Round 2**:
    - Query: `The Silent Choir war victory`
    - Status: `✅ Sufficient Evidence`
    - Found conflict resolution: **The War of Drowned Light**.
  - **Grounded Answer**:
    - Clearly states the Silent Choir won the War of Drowned Light with cited sources (`isolde_mournvale.md`, `the_war_of_drowned_light.md`).
- **Spoken Script**:
  > *"Notice what happened here: In Round 1, the agent didn't guess. It found Isolde's affiliation with The Silent Choir. The evidence checker flagged this as insufficient, generated a targeted second query for 'The Silent Choir war victory', and concluded in Round 2 with full citations."*

---

### 1:45 – 2:45 | Demo 2: Handling Contested Evidence Honestly (Question 1c_000)
- **Action**: Select preset:
  `⚖️ [1c_000 Contested Lore] State the precise year in the Age of Shadows that marks the true founding of Gloamreach.`
  Click **🔍 Search Archive**.
- **What is on screen**:
  - **Round 1**: Query `Gloamreach` &rarr; wiki records that founding is contested.
  - **Round 2**: Query `Gloamreach founding year Age of Shadows precise date` &rarr; consults the Annals and Codex.
  - **Round 3**: Query `Gloamreach established Year of the Black Dawn Age of Shadows record` &rarr; exhausts query budget.
  - **Final Answer**:
    - Explicitly refuses to hallucinate a false year.
    - Accurately states that the founding year is contested and unrecorded even in the authoritative Annals.
- **Spoken Script**:
  > *"This question is a deliberate trap in the competition corpus. Many models hallucinate a random year. Our assistant searches three times, confirms the conflict across both the wiki and codex, and honestly reports that the founding date is disputed. This satisfies the competition requirement: 'Handle conflicting evidence rather than hiding it'."*

---

### 2:45 – 3:15 | Demo 3: Schema Inspection & Robustness (Judge Verification)
- **Action**:
  - Scroll to the bottom and expand **"🔍 Inspect Official Data Contract JSON"**.
  - Highlight the exact fields: `answer`, `search_steps` (with round, query, sources_found, status), and `sources` (with source and page).
- **Spoken Script**:
  > *"Our frontend communicates strictly using the team's data contract. You can inspect the live JSON here: every search step, round count, and page-level citation is validated and ready for automated scoring."*

---

### 3:15 – 3:45 | Conclusion & Handoff
- **Spoken Script**:
  > *"In summary, Member 3's UI provides a seamless window into the assistant's decision-making process, whether running in our fast offline simulation mode or plugged into our live Groq reasoning agent. Thank you, and we welcome your questions!"*

---

## Anticipated Judge Q&A Cheat Sheet

1. **Q: What makes your solution Track 1C rather than normal RAG?**  
   *A: Normal RAG does `query -> 1 retrieval -> LLM answer`. Track 1C uses an autonomous loop: `query -> retrieval -> sufficiency check -> gap detection -> query rewrite -> repeat until grounded`.*

2. **Q: How does the evidence checker decide whether to search again?**  
   *A: It runs a structured JSON prompt evaluating whether the accumulated facts strictly answer every entity and relation in the question without guessing.*

3. **Q: Why is the search loop limited to 3 rounds?**  
   *A: To prevent infinite loops, control API latency, and prevent retrieval drift when information genuinely does not exist in the archive.*

4. **Q: How can a judge run this from a clean machine?**  
   *A: Clone the repository, run `pip install -r requirements.txt`, and execute `streamlit run src/app.py`. The simulation mode runs instantly out-of-the-box without needing any API keys.*
