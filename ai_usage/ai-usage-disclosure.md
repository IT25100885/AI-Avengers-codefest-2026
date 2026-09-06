# AI Usage Disclosure

## Project Information
- **Project**: Ashen Era Agentic Search
- **Track**: Track 1C — Searching the Way a Human Does
- **Team**: AI-Avengers (SLIIT Codefest 2026)
- **Author/Contributor**: Abdullah (Member 2)
- **AI Tool Used**: Antigravity (Google DeepMind)

## Summary of AI Assistance
AI assistance was utilized across the following areas of the codebase:
1. **LLM Client Architecture (`src/llm/client.py`)**:
   - Implementation of OpenAI-compatible Groq client with exponential backoff (`tenacity`) and fallback JSON re-prompting (`call_llm_json`).
2. **Package Refactoring & Integration**:
   - Standardizing import structures across `src/agent/`, `src/generation/`, and `src/retrieval/`.
   - Creating package `__init__.py` modules.
3. **Multi-Hop Search Pipeline Testing**:
   - Developing unit tests for planner query extraction, evidence checking, query rewriting, and answer generation.
4. **Git Branch & Conflict Resolution**:
   - Merging feature branch into `main` and resolving merge conflicts in `.env.example`, `.gitignore`, and `docs/decisions.md`.

## Detailed Logs
Complete transcripts and interaction logs are available in the `ai_usage/chat_logs/` folder:
- [Claude AI Usage Log (`ai_usage/chat_logs/claude_chat_log.txt`)](file:///Users/abdullahfawmy/Documents/GitHub/AI-Avengers-codefest-2026/ai_usage/chat_logs/claude_chat_log.txt)
- [Antigravity AI Usage Log (`ai_usage/chat_logs/antigravity_chat_log.txt`)](file:///Users/abdullahfawmy/Documents/GitHub/AI-Avengers-codefest-2026/ai_usage/chat_logs/antigravity_chat_log.txt)
