# Ashen Era Agentic Search

**SLIIT Codefest 2026 AI Competition**

## Sub-Track
**1C — Searching the Way a Human Does**

---

## Overview

Unlike standard single-turn RAG systems that query a database once and feed the result directly to an LLM, this assistant exhibits **human-like research behavior**:
1. **Plans an initial search** focused on key entities.
2. **Retrieves and evaluates evidence** for sufficiency.
3. **Identifies missing information** when evidence is incomplete or contested.
4. **Reformulates queries** to target the missing facts.
5. **Repeats up to 3 rounds** before synthesizing an honest, grounded final answer with complete source citations.

---

## Team & Roles

| Member | Name | Role & Responsibility |
|---|---|---|
| **Member 1** | Ifaza | Document Processing & Retrieval Engineer (Corpus ingestion, chunking, embeddings, vector store) |
| **Member 2** | Abdullah | Track 1C AI / Reasoning Agent Engineer (Planner, sufficiency checker, query rewriter, generator) |
| **Member 3** | Sameeha | Streamlit UI & Application Integration Engineer (Interactive web UI, multi-round visualization, demo flow) |
| **Member 4** | Rithika | Evaluation, QA, Documentation & Integration Engineer (Benchmarking, rubric scoring, test harness) |

---

## Quick Start: Launching the Application

### 1. Install Dependencies
Ensure Python 3.10+ is installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Live Mode)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your `GROQ_API_KEY` (and optional `VOYAGE_API_KEY`).

### 3. Launch Streamlit UI
Run the Streamlit application from the project root:
```bash
streamlit run src/app.py
```
Or alternatively:
```bash
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`.

---

## Streamlit UI Features (Member 3)

The user interface is designed specifically for competition demonstration and judge evaluation:
- **Dual-Engine Architecture**:
  - **Simulation Mode (Offline / Competition Demo)**: Runs instant, deterministic multi-round searches across benchmark questions without requiring external API keys. Perfect for live 3-4 minute presentations.
  - **Live Agent Pipeline**: Direct integration with Member 2's reasoning loop (`src.agent.search_agent.answer_question`) via Groq LLM.
- **Multi-Round Search Visualizer**:
  - Displays each search round clearly (Round number, Query used, Sources found).
  - Highlights sufficiency decisions (`✅ Sufficient` in green, `⚠️ Insufficient` in amber).
  - Displays query reformulation without leaking private internal system prompts.
- **Grounded Answer & Source Inspector**:
  - Formatted final answer box.
  - Granular source list with document filenames, page numbers, and category tags.
- **Competition Data Contract Inspector**:
  - Collapsible JSON expander showing the exact schema required by Section 6 of the team specification.
- **Benchmark Presets**:
  - One-click testing for multi-hop questions (1b_005), contested lore (1c_000), unrecorded artifacts (1c_003), direct lookups, and robustness checks.

---

## Running Automated Tests

Run the test suite to verify UI backend contracts and integration:
```bash
python -m unittest discover tests
```
All unit tests validate compliance with the agreed Track 1C schema.
SLIIT Codefest 2026 — Track 1C: Searching the Way a Human Does

## Overview

An AI assistant that searches the Ashen Era Archive, checks the evidence,
and performs follow-up searches until it can provide a supported answer
or reaches its search limit.

## Team

| Member | Responsibility |
|---|---|
| Ifaza | Document ingestion and retrieval |
| Abdullah | Search agent and answer generation |
| Sameeha | User interface and integration |
| Rtihika | Evaluation, QA and documentation |

## Current status

The agent and five-question evaluator run with mock retrieval.
Full-archive retrieval and end-to-end validation are still pending.

## Setup

Open the repository folder in VS Code.
Run commands in its terminal from the project root.

Python 3.13 was used during development.

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Create a local `.env` with the API settings required by
`src/llm/client.py`. Use `.env.example` as a reference if available.
Never commit real API keys.

The model used successfully during development was:

```dotenv
LLM_MODEL=openai/gpt-oss-120b
```

API credentials and the provider endpoint must also be configured.

## Run

Run the agent's example:

```powershell
py -m src.agent.search_agent
```

Run evaluation:

```powershell
py -m src.evaluation.evaluate
```

Questions: `src/evaluation/questions.json`

Results: `src/evaluation/results/`

These commands make language-model API calls.
A completed evaluation does not automatically mean the answers passed.
Scores marked `null` have not been assessed.

## Documentation

- [Decisions](docs/decisions.md)
- [Experiments and reviews](docs/experiments.md)
- [Limitations](docs/limitations.md)
- [Evaluation rubric](docs/evaluation-rubric.md)

## Remaining work

Connect real retrieval, verify answers and citations, test the UI and
clean setup, and complete the required submission deliverables.
