"""
Streamlit Web Application for Ashen Era Agentic Search.
Track 1C: Searching the Way a Human Does
SLIIT Codefest 2026 AI Competition

Built by Member 3 (Streamlit UI & Application Integration Engineer)
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

from src.ui.mock_backend import mock_answer_question

# Preset questions for fast judging and demo
PRESET_QUESTIONS = {
    "Select a preset question...": "",
    "🔥 [1b_005 Multi-Hop] Which war was won by the organization that included Isolde Mournvale as one of its members?": (
        "Which war was won by the organization that included Isolde Mournvale as one of its members?"
    ),
    "⚖️ [1c_000 Contested Lore] State the precise year in the Age of Shadows that marks the true founding of Gloamreach.": (
        "State the precise year in the Age of Shadows that marks the true founding of Gloamreach."
    ),
    "❓ [1c_003 Unrecorded Item] In which year was the 'Gauntlet of Sorrowfell' actually forged?": (
        "In which year was the 'Gauntlet of Sorrowfell' actually forged?"
    ),
    "🎯 [Direct Lookup] Which organization includes Isolde Mournvale as a member?": (
        "Which organization includes Isolde Mournvale as a member?"
    ),
    "🛡️ [Robustness / Nonsense] asdfgh qwerty zxcvbn ???": (
        "asdfgh qwerty zxcvbn ???"
    ),
}

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ashen Era | Track 1C Agentic Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished competition presentation
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .track-badge {
        background-color: #EEF2FF;
        color: #4F46E5;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.8rem;
        border: 1px solid #C7D2FE;
    }
    .step-card {
        border-radius: 0.6rem;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border: 1px solid #E2E8F0;
        background-color: #F8FAFC;
    }
    .step-sufficient {
        border-left: 5px solid #10B981;
    }
    .step-insufficient {
        border-left: 5px solid #F59E0B;
    }
    .status-badge-sufficient {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-insufficient {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .answer-box {
        background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
        border: 1px solid #86EFAC;
        border-radius: 0.75rem;
        padding: 1.3rem;
        margin: 1rem 0;
    }
    .source-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "preset_choice" not in st.session_state:
    st.session_state.preset_choice = "Select a preset question..."


# -----------------------------------------------------------------------------
# Backend Invocation Handlers
# -----------------------------------------------------------------------------
def run_live_pipeline(question: str) -> Dict[str, Any]:
    """Execute live reasoning agent from Member 2's src.agent.search_agent."""
    from src.agent.search_agent import answer_question
    return answer_question(question)


def execute_search(question: str, mode: str) -> Optional[Dict[str, Any]]:
    """Execute query via selected backend with friendly error handling."""
    clean_q = question.strip()
    if not clean_q:
        st.warning("⚠️ Please enter a question or select a preset before searching.")
        return None

    result = None
    start_time = time.time()

    if mode == "Simulation Mode (Offline / Competition Demo)":
        with st.spinner("Executing human-like iterative search simulation..."):
            time.sleep(0.6)  # Realistic presentation pacing
            result = mock_answer_question(clean_q)
    else:
        with st.spinner("Connecting to Live Reasoning Agent (Groq LLM + Archive)..."):
            try:
                result = run_live_pipeline(clean_q)
            except ValueError as ve:
                st.error(
                    f"⚠️ Live Agent Configuration Notice: {ve}\n\n"
                    "Tip: Switch to **Simulation Mode** in the sidebar to run without external API keys!"
                )
                return None
            except Exception as e:
                st.error(
                    f"⚠️ Live Agent Encountered an Error: {str(e)}\n\n"
                    "Falling back to Simulation Mode for this query..."
                )
                result = mock_answer_question(clean_q)

    elapsed = round(time.time() - start_time, 2)
    if result:
        result["elapsed_time"] = elapsed
        result["question"] = clean_q
        result["mode"] = mode

        # Store in session state and history
        st.session_state.last_result = result
        st.session_state.history.append(result)

    return result


# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Control Panel")

    st.markdown("### Backend Engine")
    backend_mode = st.radio(
        "Select Active Engine:",
        [
            "Simulation Mode (Offline / Competition Demo)",
            "Live Agent Pipeline (src.agent.search_agent)",
        ],
        index=0,
        help="Simulation Mode runs deterministic multi-round traces without API keys. Live Agent calls Groq and the real pipeline.",
    )

    # Health check for API key
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("your_"):
        st.success("🟢 GROQ API Key: Configured")
    else:
        st.info("ℹ️ GROQ API Key: Not set (Simulation Mode ready)")

    st.markdown("---")
    st.markdown("### Agent Parameters")
    max_rounds = st.slider("Max Search Rounds", min_value=1, max_value=5, value=3)
    top_k = st.slider("Retrieval Top-K", min_value=5, max_value=25, value=15)
    os.environ["MAX_SEARCH_ROUNDS"] = str(max_rounds)
    os.environ["SEARCH_TOP_K"] = str(top_k)

    st.markdown("---")
    st.markdown("### Team & Project")
    st.markdown(
        """
        - **Track**: 1C — Searching the Way a Human Does
        - **Team**: AI Avengers
        - **Member 1**: Ifaza (Ingestion & Retrieval)
        - **Member 2**: Abdullah (Reasoning Agent)
        - **Member 3**: Sameeha (Streamlit UI & Integration)
        - **Member 4**: Rithika (Evaluation & QA)
        """
    )

    if st.button("🧹 Clear Session History", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_result = None
        st.rerun()


# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------
st.markdown('<span class="track-badge">SLIIT CODEFEST 2026 • SUB-TRACK 1C</span>', unsafe_allow_html=True)
st.markdown('<div class="main-header">⚔️ Ashen Era: Agentic Search Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Demonstrating iterative research behavior: <em>search &rarr; inspect evidence &rarr; detect gaps '
    '&rarr; reformulate query &rarr; repeat until grounded answer</em>'
    '</div>',
    unsafe_allow_html=True,
)

# Preset Question Selector
col_preset, col_btn = st.columns([4, 1])
with col_preset:
    selected_preset = st.selectbox(
        "Choose a competition benchmark question or type below:",
        options=list(PRESET_QUESTIONS.keys()),
        index=0,
    )

# Manage question synchronization
if selected_preset != "Select a preset question..." and PRESET_QUESTIONS[selected_preset]:
    user_input = st.text_area(
        "User Question:",
        value=PRESET_QUESTIONS[selected_preset],
        height=75,
        placeholder="Enter a question about the Ashen Era Archive...",
    )
else:
    user_input = st.text_area(
        "User Question:",
        value=st.session_state.current_question,
        height=75,
        placeholder="Enter a question about the Ashen Era Archive...",
    )

col_action1, col_action2, _ = st.columns([1.5, 1, 4])
with col_action1:
    search_clicked = st.button("🔍 Search Archive", type="primary", use_container_width=True)
with col_action2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.current_question = ""
        st.session_state.last_result = None
        st.rerun()

# Run search on button click
if search_clicked:
    st.session_state.current_question = user_input
    execute_search(user_input, backend_mode)


# -----------------------------------------------------------------------------
# Display Active Search Results
# -----------------------------------------------------------------------------
current_res = st.session_state.last_result

if current_res:
    st.markdown("---")
    st.subheader("📊 Search Execution & Evidence Trail")

    search_steps: List[Dict[str, Any]] = current_res.get("search_steps", [])
    sources: List[Dict[str, Any]] = current_res.get("sources", [])
    answer_text: str = current_res.get("answer", "")
    elapsed = current_res.get("elapsed_time", 0.0)

    # Metrics Summary Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Search Rounds", len(search_steps))
    with m2:
        total_retrieved = sum(s.get("sources_found", 0) for s in search_steps)
        st.metric("Total Documents Inspected", total_retrieved)
    with m3:
        final_status = search_steps[-1]["status"] if search_steps else "unknown"
        st.metric("Final Evidence Status", final_status.capitalize())
    with m4:
        st.metric("Execution Time", f"{elapsed}s")

    # Multi-Round Timeline Visualization
    st.markdown("#### 🔄 Iterative Search Rounds")
    for step in search_steps:
        r_num = step.get("round", 1)
        query = step.get("query", "")
        count = step.get("sources_found", 0)
        status = step.get("status", "insufficient")
        missing_info = step.get("missing_info")

        is_sufficient = (status == "sufficient")
        card_class = "step-sufficient" if is_sufficient else "step-insufficient"
        badge_html = (
            '<span class="status-badge-sufficient">✅ Sufficient Evidence</span>'
            if is_sufficient
            else '<span class="status-badge-insufficient">⚠️ Insufficient Evidence (Searching Again)</span>'
        )

        st.markdown(
            f"""
            <div class="step-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>Round {r_num} Search</strong>
                    {badge_html}
                </div>
                <div><strong>Query Used:</strong> <code>{query}</code></div>
                <div style="color: #475569; font-size: 0.9rem; margin-top: 0.3rem;">
                    <strong>Retrieved Chunks:</strong> {count} documents
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if missing_info and not is_sufficient:
            st.caption(f"💡 *Agent Decision Trail:* {missing_info}")

    # Grounded Final Answer Section
    st.markdown("#### 📜 Grounded Final Answer")
    st.markdown(
        f"""
        <div class="answer-box">
            {answer_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cited Sources Section
    st.markdown("#### 📚 Citations & Authoritative Sources")
    if sources:
        cols = st.columns(2)
        for idx, src in enumerate(sources):
            col_idx = idx % 2
            with cols[col_idx]:
                doc_name = src.get("source", "Unknown Document")
                page_info = f"Page {src.get('page')}" if src.get("page") is not None else "Page N/A"
                cat = src.get("category", "Archive Record")
                st.markdown(
                    f"""
                    <div class="source-card">
                        📄 <strong>{doc_name}</strong> &nbsp;•&nbsp; <code>{page_info}</code>
                        <div style="font-size: 0.8rem; color: #64748B;">Category: {cat}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No authoritative sources could be matched to the query.")

    # Data Contract Inspector for Judges
    with st.expander("🔍 Inspect Official Data Contract JSON (Sub-track 1C Specification)"):
        clean_contract = {
            "answer": answer_text,
            "search_steps": [
                {
                    "round": s["round"],
                    "query": s["query"],
                    "sources_found": s["sources_found"],
                    "status": s["status"],
                }
                for s in search_steps
            ],
            "sources": [
                {"source": s["source"], "page": s.get("page")}
                for s in sources
            ],
        }
        st.json(clean_contract)


# -----------------------------------------------------------------------------
# Historical Search Trail (for 3-4 minute presentation)
# -----------------------------------------------------------------------------
if len(st.session_state.history) > 1:
    st.markdown("---")
    st.subheader("🗂️ Session Question History")
    with st.expander(f"Review previous questions ({len(st.session_state.history)} searches executed)"):
        for i, item in enumerate(reversed(st.session_state.history[:-1])):
            st.markdown(f"**Q{len(st.session_state.history)-1-i}:** *{item.get('question')}*")
            st.caption(f"Rounds: {len(item.get('search_steps', []))} | Sources: {len(item.get('sources', []))}")
            st.markdown("---")
