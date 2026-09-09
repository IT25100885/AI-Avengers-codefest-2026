
# SLIIT Codefest 2026 — Track 1C Demonstration Script

**Team:** AI Avengers  
**System:** Ashen Era Agentic Search  
**Sub-track:** 1C — Searching the Way a Human Does

## Important Demo Rule

The final competition video must include a genuine live, unedited end-to-end demonstration using the **Live Agent Pipeline** and real archive retrieval.

Simulation Mode may be shown briefly as an offline testing feature, but it should not be presented as the real live system.

## Suggested Live Demo Flow

### 0:00–0:40 — Problem

Spoken explanation:

> We selected Sub-track 1C because archive questions often require more than one search. Our system works like a human researcher: it searches, checks the evidence, detects what is missing, rewrites the query, searches again, and only then produces a grounded answer.

### 0:40–1:10 — Architecture

Show the architecture diagram and explain:

```text
Question
→ Planner
→ Voyage Query Embedding
→ ChromaDB Retrieval
→ Voyage Reranking
→ Evidence Sufficiency Check
→ Query Rewrite if needed
→ Grounded Answer
```

Mention that Groq powers reasoning and Voyage AI + ChromaDB power semantic retrieval.

### 1:10–2:30 — Live Real-Input Demo 1

Switch the UI to:

```text
Live Agent Pipeline (src.agent.search_agent)
```

Use:

```text
State the precise year in the Age of Shadows that marks the true founding of Gloamreach.
```

Show:

- search query
- retrieved evidence
- sufficiency decision
- rewritten query if required
- final grounded answer
- cited archive sources

Do not narrate a specific number of rounds in advance; describe what the real run actually does.

### 2:30–3:40 — Live Real-Input Demo 2

Use:

```text
In which year was the 'Gauntlet of Sorrowfell' actually forged?
```

Again show the actual search trail and sources produced by Live Mode.

### 3:40–4:20 — Multi-Hop Behavior

Use:

```text
Which war was won by the organization that included Isolde Mournvale as one of its members?
```

Explain how the system may first identify the organization and then search for the war associated with that organization.

### 4:20–4:50 — Controls and Transparency

Show:

- Max Search Rounds
- Retrieval Top-K
- source/citation display
- JSON data-contract inspector
- transparent error handling

### 4:50–5:20 — Limitations

Briefly mention:

- image-only content is not OCR-indexed
- standalone PNG figure plates are not in the text index
- generated vector index is local and not committed
- external APIs can be affected by rate limits

### 5:20–5:40 — Team Roles

- Ifaza — ingestion and retrieval
- Abdullah — reasoning agent
- Sameeha — UI and integration
- Rithika — evaluation, QA and documentation

## Judge Q&A

### What makes this Track 1C instead of normal RAG?

Normal single-turn RAG typically performs one retrieval and immediately asks the LLM to answer.

Our system performs an iterative loop:

```text
retrieve
→ inspect evidence
→ detect missing information
→ rewrite query
→ retrieve again
→ answer when sufficient
```

### What retrieval does Live Mode actually use?

Live Mode calls the real search module:

```python
from src.retrieval.search import search
```

That module uses Voyage AI query embeddings, ChromaDB vector retrieval and Voyage reranking.

### Why do you still have Simulation Mode?

Simulation Mode is an explicit offline testing and presentation-support feature.

It is clearly labeled and does not silently replace failed live execution.

### How does a judge run Live Mode?

1. Install `requirements.txt`.
2. Add `GROQ_API_KEY` and `VOYAGE_API_KEY` to `.env`.
3. Place the Ashen Era Archive at `data/corpus/Ashen_Era_Archive/`.
4. Run `python -m src.retrieval.index_corpus`.
5. Run `streamlit run src/app.py`.
6. Select Live Agent Pipeline.
