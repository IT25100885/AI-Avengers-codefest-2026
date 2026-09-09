# AI-Avengers — Ashen Era Agentic Search
## SLIIT Codefest 2026 AI Competition

**Sub-track:** 1C — Searching the Way a Human Does  
**Demo Video:** [ADD UNLISTED YOUTUBE LINK AFTER RECORDING]

---

## 1. Problem Statement

The Ashen Era Archive contains hundreds of interconnected documents across PDF, DOCX, Markdown, plain text, and scanned formats.

Many questions cannot be answered using a single search because relevant facts may be spread across multiple documents, and different archive sources may disagree.

For Sub-track 1C, our goal was to build an assistant that searches iteratively like a human researcher: it retrieves evidence, evaluates whether the evidence is sufficient, identifies what is still missing, reformulates its search, and continues until it can produce a grounded answer.

---

## 2. Solution Overview

Our system uses an agentic multi-round document-search pipeline.

The process is:

```text
User Question
      |
      v
Initial Query Planner
      |
      v
Voyage Query Embedding
      |
      v
ChromaDB Retrieval
      |
      v
Voyage Reranking
      |
      v
Evidence Sufficiency Check
      |
      +----------------------+
      |                      |
 Insufficient             Sufficient
      |                      |
      v                      v
Query Rewriter         Answer Generator
      |
      v
Search Again

---

## 3. Key Technical Decisions

### Iterative Search Instead of Single-Turn RAG
We selected an iterative agentic search approach because Track 1C requires the system to reason between searches. After each retrieval round, the agent checks whether the collected evidence is sufficient. If information is missing, it reformulates the query and searches again.

### Voyage AI Embeddings
Voyage AI is used to create vector embeddings for document chunks and user queries. This allows semantic retrieval even when the wording of the question differs from the wording in the archive.

### ChromaDB Vector Store
ChromaDB was selected as the persistent vector database because it supports local storage, cosine-similarity retrieval, and repeated searches without rebuilding the index every time.

### Voyage Reranking
Initial ChromaDB results are reranked so that the strongest evidence is prioritized before it is passed to the reasoning agent.

### Groq LLM
Groq provides the LLM used for query planning, evidence sufficiency checking, query rewriting, and grounded answer generation.

### Search-Round Limit
A configurable maximum search-round limit is used to prevent endless search loops while still allowing the agent to perform multiple searches when necessary.

---

## 4. What Works

The implemented system currently supports:

- Loading PDF, DOCX, Markdown, and plain-text archive documents.
- Splitting extracted content into searchable chunks while preserving metadata.
- Generating semantic embeddings with Voyage AI.
- Persisting indexed chunks in ChromaDB.
- Semantic retrieval followed by Voyage reranking.
- Initial query planning.
- Multi-round evidence accumulation.
- Evidence sufficiency checking.
- Query rewriting when information is incomplete.
- Grounded answer generation with source information.
- A Streamlit interface that visualizes the search process.
- Configurable search rounds and retrieval Top-K.
- Automated evaluation scripts and stored evaluation results.
- Simulation mode for deterministic demonstration and live mode for the real agent pipeline.

During the final corpus indexing process, 1,440 document/page entries were successfully loaded and converted into 2,186 searchable chunks.

**Final live evaluation results will be added after corpus indexing and end-to-end validation are completed.**

---

## 5. Limitations

The current system has several known limitations:

- Standalone image files are not currently indexed. During ingestion, 86 unsupported files, mainly PNG figure plates, were skipped.
- Image-only or scanned content without extractable text may not be searchable because OCR is not currently implemented.
- Exact page numbers cannot always be recovered reliably from DOCX documents.
- Live mode depends on external Groq and Voyage AI services and may be affected by API rate limits, network failures, or provider availability.
- The agent has a fixed maximum number of search rounds, so especially difficult questions may require more searches than allowed.
- Conflicting archive sources can affect answer quality when the most authoritative evidence is not retrieved.

A more detailed limitation analysis is available in `docs/limitations.md`.

---

## 6. Evaluation and Validation

The evaluation harness runs benchmark questions through the same `answer_question()` interface used by the live reasoning agent.

For each question, it records:

- generated answer
- search rounds
- queries used
- retrieved sources
- expected answer
- reviewer scoring and notes

The evaluation set includes official Track 1C questions as well as multi-hop, direct-lookup, and robustness tests.

Earlier development evaluations were used to identify weaknesses in retrieval and agent behavior. A final evaluation using the fully indexed Ashen Era Archive will be performed after indexing is complete.

**Final results:** [ADD AFTER FINAL LIVE EVALUATION]

---

## 7. AI Usage Disclosure

AI tools were used throughout development as coding, debugging, review, and documentation assistants.

The team used tools including ChatGPT, Claude, Cursor, and Antigravity for tasks such as:

- document-processing development
- retrieval and embedding implementation
- reasoning-agent development
- Streamlit UI implementation
- debugging and integration
- evaluation and QA
- documentation and competition preparation

All AI-assisted outputs were reviewed, tested, and modified by team members before inclusion in the project.

Detailed AI usage information and development chat logs are available in the `ai_usage/` directory.

---

## 8. Team Contributions

| Member | Role | Main Contribution |
|---|---|---|
| Ifaza | Document Processing & Retrieval | Ingestion, chunking, metadata, Voyage embeddings, ChromaDB retrieval and reranking |
| Abdullah | AI & Reasoning Agent | LLM client, search planner, evidence checker, query rewriter and iterative search loop |
| Sameeha | UI & Application Integration | Streamlit interface, backend integration, search visualization and demo preparation |
| Rithika | Evaluation, QA & Documentation | Evaluation harness, benchmark testing, QA, limitation analysis and submission documentation |

---

## 9. Conclusion

Ashen Era Agentic Search demonstrates the core requirement of Track 1C: searching in multiple stages rather than relying on one retrieval attempt.

The system plans a search, retrieves evidence, evaluates what is still missing, reformulates its query when necessary, accumulates evidence across rounds, and finally produces a grounded answer.

This approach is designed to better handle questions whose answers require investigation across the interconnected Ashen Era Archive.