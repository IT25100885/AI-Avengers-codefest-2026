# Ashen Era Agentic Search

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