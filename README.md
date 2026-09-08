# Ashen Era Agentic Search

**SLIIT Codefest 2026 AI Competition**  
**Sub-Track**: 1C — Searching the Way a Human Does  

---

## Overview

Unlike standard single-turn RAG systems that execute one embedding query and feed the output directly to an LLM, this assistant demonstrates **autonomous, human-like iterative research behavior**:
1. **Initial Search Planning**: Extracts the primary named entity to start the investigation.
2. **Evidence Sufficiency Judgment**: Evaluates retrieved facts to determine if the specific question can be fully and conclusively answered without guessing.
3. **Information Gap Detection**: Flags missing connections or contested claims across archive documents.
4. **Targeted Query Reformulation**: Formulates new search queries to bridge identified evidence gaps.
5. **Multi-Round Evidence Accumulation**: Searches up to an assigned round budget (default 3 rounds) before synthesizing an authoritative, grounded answer with granular citations.

---

## Team & Roles

| Member | Name | Responsibility & Modules |
|---|---|---|
| **Member 1** | Ifaza | **Document Processing & Retrieval**: Ingestion (`src/ingestion/`), chunking, metadata preservation, Voyage AI embeddings, ChromaDB vector store (`src/retrieval/`). |
| **Member 2** | Abdullah | **AI & Reasoning Agent**: Groq LLM client (`src/llm/client.py`), search planner (`src/agent/planner.py`), sufficiency checker (`src/agent/evidence_checker.py`), query rewriter (`src/agent/query_rewriter.py`), and search agent loop (`src/agent/search_agent.py`). |
| **Member 3** | Sameeha | **Streamlit UI & Application Integration**: Interactive web UI (`src/app.py`), multi-round search visualization, simulation engine (`src/ui/mock_backend.py`), slider parameter integration, and live demo preparation (`docs/demo_script.md`). |
| **Member 4** | Rithika | **Evaluation, QA & Documentation**: Evaluation harness (`src/evaluation/evaluate.py`), benchmark questions (`src/evaluation/questions.json`), rubric scoring, and limitation analysis. |

---

## Architecture & Execution Modes

The application provides two operational modes via the sidebar toggle:

### 1. Simulation Mode (Offline / Competition Demo)
- **Purpose**: Provides instant, deterministic multi-round demonstration traces for competition presentations and offline testing without requiring active API keys.
- **Supported Questions**: Pre-configured for official benchmark questions:
  - `1b_005 Multi-Hop`: Isolde Mournvale &rarr; The Silent Choir &rarr; War of Drowned Light (2 rounds).
  - `1c_000 Multi-Round Benchmark`: Gloamreach founding year &rarr; resolved to **246 AS** via Codex Vaeloria I (p. 23) (2 rounds).
  - `1c_003 Multi-Round Benchmark`: Gauntlet of Sorrowfell forging date &rarr; resolved to **391 AS** via Codex Vaeloria II (p. 11) (2 rounds).
  - `Direct Lookup`: Isolde Mournvale membership &rarr; The Silent Choir (1 round).
  - `Robustness Test`: Gibberish input handling (1 round, polite rejection).
- **Boundaries**: Arbitrary custom questions return a clear refusal: *"No simulation available for this question. Please switch to Live Agent Pipeline."* No answers or search traces are invented.
- **Controls**: Parameter sliders are disabled in simulation mode as traces are pre-computed.

### 2. Live Agent Pipeline (`src.agent.search_agent`)
- **Purpose**: Executes the live LLM reasoning loop using Groq and the OpenAI-compatible client with exponential backoff (`tenacity`).
- **Parameter Controls**: Sidebar sliders for **Max Search Rounds** and **Retrieval Top-K** are dynamically passed into each search execution.
- **Retrieval Status**: Live Mode currently operates using the live Groq LLM reasoning loop over the structured archive test retrieval module (`src.retrieval.mock_search`). Full-archive ChromaDB + Voyage AI embedding retrieval is currently being integrated by Member 1 to replace mock retrieval.
- **Error Boundaries**: If live API execution fails (e.g. missing `GROQ_API_KEY`, rate limits, or network timeout), the UI displays the error transparently without silent fallback to mock data.

---

## Quick Start & Setup

### 1. Environment Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (for Live Agent Mode)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Set your Groq API credentials:
```dotenv
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=openai/gpt-oss-120b
```
*(Note: Simulation Mode runs completely out-of-the-box without an API key).*

### 3. Launch the Streamlit Web UI
Run the application from the project root:
```bash
streamlit run src/app.py
```
Alternatively:
```bash
streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.

---

## Running CLI & Evaluation Scripts

### Execute Live Agent via CLI
Run the standalone search agent example:
```bash
python -m src.agent.search_agent
```

### Run Automated Unit Tests
Run the comprehensive test suite covering data contracts, parameter passing, and error boundaries:
```bash
python -m unittest discover tests
```

### Run Evaluation Suite
Execute the 5-question evaluation harness:
```bash
python -m src.evaluation.evaluate
```
Results are timestamped and saved in `src/evaluation/results/`.

---

## Documentation Links

- **[Decisions Log](docs/decisions.md)**: Architectural decisions and evolution records.
- **[Live Demo Script](docs/demo_script.md)**: 3-4 minute presentation walkthrough and judge Q&A guide.
- **[Experiments & Results](docs/experiments.md)**: Benchmark logs and prompt experimentation.
- **[System Limitations](docs/limitations.md)**: Documented system constraints and failure modes.
- **[Evaluation Rubric](docs/evaluation-rubric.md)**: Scoring guidelines for Track 1C evaluation.
- **[AI Usage Disclosure](ai_usage/ai-usage-disclosure.md)**: Full disclosure of AI-assisted engineering and chat logs.
