# AI Usage Disclosure

## Project Information
- **Project**: Ashen Era Agentic Search
- **Track**: Track 1C — Searching the Way a Human Does
- **Team**: AI-Avengers (SLIIT Codefest 2026)
- **Author/Contributor**: Abdullah (Member 2), Sameeha (Member 3)
- **AI Tool Used**: Antigravity (Google DeepMind), Claude (Anthropic)

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
5. **Streamlit UI & Integration (Member 3 - Sameeha)**:
   - Development of `src/app.py`, `app.py`, and `src/ui/mock_backend.py`.
   - Iterative search round visualizer with evidence sufficiency statuses (`sufficient` / `insufficient`) and granular citation cards.
   - Dual-backend design enabling switching between live agent pipeline and deterministic simulation mode.
   - Dynamic parameter passing (`max_rounds`, `top_k`) from sidebar sliders to live reasoning agent.
   - Elimination of silent fallbacks; enforcement of strict simulation boundaries for unsupported questions.
   - Automated contract validation test suite in `tests/test_ui_backend.py`.
   - Live demo script and judge presentation materials in `docs/demo_script.md`.

## Detailed Logs
Complete transcripts and interaction logs are available in the `ai_usage/chat_logs/` folder:
- [Claude AI Usage Log (`ai_usage/chat_logs/claude_chat_log.txt`)](file:///Users/abdullahfawmy/Documents/GitHub/AI-Avengers-codefest-2026/ai_usage/chat_logs/claude_chat_log.txt)
- [Antigravity AI Usage Log - Member 2 (`ai_usage/chat_logs/antigravity_chat_log.txt`)](file:///Users/abdullahfawmy/Documents/GitHub/AI-Avengers-codefest-2026/ai_usage/chat_logs/antigravity_chat_log.txt)
- [Antigravity AI Usage Log - Member 3 UI (`ai_usage/chat_logs/member3_ui_antigravity_chat_log.txt`)](file:///c:/Users/Dell/Desktop/AI%20Avengers/AI-Avengers-codefest-2026/ai_usage/chat_logs/member3_ui_antigravity_chat_log.txt)
