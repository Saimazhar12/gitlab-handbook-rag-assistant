"""
app.py
------
Streamlit interface.

Chat UI over the GitLab Handbook RAG chatbot. Run with:

    streamlit run app.py

Visual identity: a premium dark-navy "AI SaaS product" look -- see the
"Design" section in README.md for the full palette/rationale. This file
only handles presentation; all retrieval/LLM/citation logic lives in
src/rag_chain.py and is untouched by the redesign.

Handles the common edge cases gracefully in the UI itself:
  - Chroma DB not built yet          -> friendly setup instructions, no crash
  - Missing API key                  -> friendly setup instructions, no crash
  - Empty input                      -> chat_input already prevents blank submits
  - LLM/embedding API errors at query time -> caught inside rag_chain, shown as
    a normal chat message rather than a stack trace
"""

import os
import sys
import base64
import textwrap

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def render_html(html: str) -> None:
    """st.markdown(..., unsafe_allow_html=True), but safe against Markdown's
    'four-space indent = code block' rule. Multi-line HTML written inside an
    indented triple-quoted string keeps that indentation when the string is
    built -- and Markdown then renders those lines as a literal code block
    instead of parsing the HTML, showing raw tags on screen. textwrap.dedent
    strips the common leading whitespace before handing it to st.markdown."""
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

SUGGESTIONS = [
    "How does GitLab define its mission?",
    "What are GitLab's company values?",
    "How does GitLab work remotely?",
    "What is GitLab's approach to collaboration?",
]


def _logo_data_uri() -> str:
    """Base64-encode the logo so it can be embedded directly in custom HTML."""
    try:
        with open(LOGO_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return ""


LOGO_URI = _logo_data_uri()

st.set_page_config(
    page_title="SafeX Handbook Assistant",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "📘",
    layout="centered",
)

# --- Visual identity -------------------------------------------------------
# Palette: dark navy base (#0B1120), layered surfaces (#111827 / #151F32),
# indigo/violet accent pair (#6366F1 / #8B5CF6), used sparingly. Inter for
# UI text -- clean, modern, standard for this kind of product UI.
render_html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0B1120;
        --bg-secondary: #111827;
        --card: #151F32;
        --border: #263248;
        --accent: #6366F1;
        --accent-2: #8B5CF6;
        --text: #F8FAFC;
        --text-muted: #94A3B8;
        --success: #22C55E;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }

    /* Base app background: dark navy with two very subtle glow blobs */
    .stApp {
        background-color: var(--bg);
        background-image:
            radial-gradient(circle at 15% 8%, rgba(99, 102, 241, 0.10) 0%, transparent 40%),
            radial-gradient(circle at 85% 15%, rgba(139, 92, 246, 0.08) 0%, transparent 38%);
        background-attachment: fixed;
    }

    /* Blend Streamlit's default top header into our background instead of
       hiding it outright -- keeps the mobile sidebar-toggle control working. */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    #MainMenu, footer { visibility: hidden; }

    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: var(--text); }

    /* ---- Sidebar brand ---- */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2px;
    }
    .sidebar-brand img {
        width: 34px;
        height: 34px;
        border-radius: 9px;
    }
    .sidebar-brand-text span.name {
        display: block;
        font-weight: 600;
        font-size: 1.0rem;
        color: var(--text);
    }
    .sidebar-brand-text span.sub {
        display: block;
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    .sidebar-section-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 18px 0 8px 0;
    }
    .sidebar-about {
        font-size: 0.86rem;
        color: var(--text-muted);
        line-height: 1.5;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
    }

    /* ---- Tech badges ---- */
    .badge-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
    .badge {
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--text-muted);
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 4px 10px;
    }

    /* ---- Status card ---- */
    .status-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 4px;
    }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--success);
        margin-right: 7px;
        box-shadow: 0 0 6px rgba(34, 197, 94, 0.7);
    }
    .status-title { font-size: 0.86rem; font-weight: 500; color: var(--text); }
    .status-sub { font-size: 0.78rem; color: var(--text-muted); margin: 4px 0 0 15px; }

    .sidebar-footer {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-align: center;
        margin-top: 10px;
    }

    /* ---- Main header ---- */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0 20px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 22px;
    }
    .app-header-left { display: flex; align-items: center; gap: 14px; }
    .app-header img {
        width: 44px; height: 44px;
        border-radius: 12px;
        flex-shrink: 0;
    }
    .app-title { font-weight: 700; font-size: 1.35rem; color: var(--text); margin: 0; }
    .app-tagline { font-size: 0.82rem; color: var(--text-muted); margin: 2px 0 0 0; }
    .header-status {
        font-size: 0.78rem;
        color: var(--text-muted);
        white-space: nowrap;
    }

    /* ---- Empty state ---- */
    .empty-state { text-align: center; padding: 36px 12px 24px 12px; }
    .empty-state-icon {
        width: 60px; height: 60px;
        border-radius: 16px;
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 18px auto;
        font-size: 28px;
    }
    .empty-state h2 { font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0 0 8px 0; }
    .empty-state p { font-size: 0.92rem; color: var(--text-muted); max-width: 460px; margin: 0 auto 26px auto; line-height: 1.5; }

    /* Suggestion "cards" are real st.button elements underneath, styled via
       their per-container key class (Streamlit 1.3x+ st.container(key=...)). */
    div[data-testid="stButton"] button {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        text-align: left !important;
        padding: 12px 14px !important;
        font-size: 0.86rem !important;
        font-weight: 400 !important;
        transition: border-color 0.15s ease, transform 0.15s ease;
        width: 100%;
    }
    div[data-testid="stButton"] button:hover {
        border-color: var(--accent) !important;
        color: var(--text) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] button:focus:not(:active) {
        border-color: var(--accent) !important;
        color: var(--text) !important;
    }

    /* Clear-conversation button gets a slightly different look */
    .st-key-clear_btn_wrap div[data-testid="stButton"] button {
        text-align: center !important;
        color: var(--text-muted) !important;
        font-size: 0.82rem !important;
    }

    /* ---- Chat messages ---- */
    .msg-row { display: flex; margin-bottom: 16px; gap: 10px; }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.assistant { justify-content: flex-start; align-items: flex-start; }

    .msg-avatar {
        width: 30px; height: 30px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        display: flex; align-items: center; justify-content: center;
        font-size: 15px;
        flex-shrink: 0;
    }

    .msg-bubble {
        max-width: 76%;
        padding: 12px 16px;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .msg-bubble p:last-child { margin-bottom: 0; }

    .msg-bubble.user {
        background: var(--accent);
        color: #FFFFFF;
        border-radius: 14px 14px 3px 14px;
    }
    .msg-bubble.assistant {
        background: var(--card);
        border: 1px solid var(--border);
        color: var(--text);
        border-radius: 3px 14px 14px 14px;
    }

    .msg-row.newest .msg-bubble { animation: rise-in 0.3s ease-out; }
    @keyframes rise-in {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ---- Sources ---- */
    .sources-tab {
        margin-top: 10px;
        border-top: 1px solid var(--border);
        padding-top: 8px;
    }
    .sources-tab summary {
        cursor: pointer;
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--accent-2);
        list-style: none;
    }
    .sources-tab summary::-webkit-details-marker { display: none; }
    .source-item {
        display: flex;
        gap: 8px;
        font-size: 0.82rem;
        color: var(--text-muted);
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 8px;
    }
    .citation-badge {
        flex-shrink: 0;
        width: 18px; height: 18px;
        border-radius: 5px;
        background: var(--accent);
        color: #fff;
        font-size: 0.68rem;
        font-weight: 600;
        display: flex; align-items: center; justify-content: center;
    }
    .source-item strong { color: var(--text); }
    .source-item a { color: var(--accent-2); text-decoration: none; word-break: break-all; }
    .source-item a:hover { text-decoration: underline; }

    /* ---- Chat input ---- */
    /* Streamlit wraps the chat input in a sticky bottom container that has
       its own (light) background — override every layer, not just the
       textarea, or a white bar shows through around/behind it. */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: var(--bg) !important;
    }
    [data-testid="stChatInput"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea {
        background: var(--card) !important;
        border: none !important;
        color: var(--text) !important;
        border-radius: 14px !important;
        caret-color: var(--text) !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }
    [data-testid="stChatInput"]:focus-within {
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        border-radius: 14px;
    }
    /* the send button on the right side of the input */
    [data-testid="stChatInput"] button {
        background: transparent !important;
    }
    [data-testid="stChatInput"] svg {
        fill: var(--text-muted) !important;
    }

    /* ---- Responsiveness ---- */
    @media (max-width: 640px) {
        .msg-bubble { max-width: 88%; }
        .app-title { font-size: 1.15rem; }
        .header-status { display: none; }
    }
    </style>
    """
)


@st.cache_resource(show_spinner="Loading knowledge base and model...")
def load_bot():
    from rag_chain import RagChatbot
    return RagChatbot()


# --- Boot the chatbot, with a friendly error screen instead of a crash ---
try:
    bot = load_bot()
except Exception as exc:
    st.error(
        "**The chatbot isn't ready yet.**\n\n"
        f"Details: `{type(exc).__name__}: {exc}`\n\n"
        "Checklist:\n"
        "1. Have you run `python src/scrape.py` and `python src/clean.py`?\n"
        "2. Have you run `python src/ingest.py` to build the Chroma database?\n"
        "3. Does your `.env` file have a valid `OPENAI_API_KEY` or "
        "`GOOGLE_API_KEY`, matching `LLM_PROVIDER`?\n\n"
        "See `.env.example` and the README for setup steps."
    )
    st.stop()

# Page count shown in the sidebar/header status -- read from the actual
# source registry rather than hardcoded, so it can't go stale again.
try:
    from sources import SOURCES
    PAGE_COUNT = len(SOURCES)
except Exception:
    PAGE_COUNT = "—"

# --- Main header ---
render_html(
    f"""
    <div class="app-header">
        <div class="app-header-left">
            <img src="{LOGO_URI}" alt="SafeX Handbook Assistant logo" />
            <div>
                <p class="app-title">SafeX Handbook Assistant</p>
                <p class="app-tagline">Your AI-powered GitLab Handbook knowledge assistant</p>
            </div>
        </div>
        <div class="header-status">
            <span class="status-dot"></span>Knowledge Base Online
        </div>
    </div>
    """
)


def render_sources_html(sources) -> str:
    if not sources:
        return ""
    items = []
    for i, src in enumerate(sources, start=1):
        section = f" — {src['section']}" if src.get("section") else ""
        link = f'<br><a href="{src["source_url"]}" target="_blank">{src["source_url"]}</a>' if src.get("source_url") else ""
        items.append(
            f'<div class="source-item">'
            f'<span class="citation-badge">{i}</span>'
            f'<span><strong>{src["title"]}</strong>{section}{link}</span>'
            f'</div>'
        )
    return (
        '<details class="sources-tab"><summary>📚 Sources</summary>'
        + "".join(items)
        + "</details>"
    )


def render_message(role: str, content: str, sources=None, newest: bool = False):
    row_class = f"msg-row {role}" + (" newest" if newest else "")
    bubble_class = f"msg-bubble {role}"
    avatar_html = '<div class="msg-avatar">📘</div>' if role == "assistant" else ""
    sources_html = render_sources_html(sources) if role == "assistant" else ""
    # Built as one flat line (no newlines/indentation) on purpose: when
    # avatar_html is empty (user messages), the multi-line/indented version
    # left a blank line followed by an indented line, which Markdown reads
    # as the start of a code block -- printing the raw <div> tags instead
    # of rendering them. A single-line string has no blank/indented lines
    # for that rule to trigger on.
    html = (
        f'<div class="{row_class}">'
        f'{avatar_html}'
        f'<div class="{bubble_class}">{content}{sources_html}</div>'
        f'</div>'
    )
    render_html(html)


def ask(question: str):
    """Shared submit path for both the chat_input box and suggestion cards,
    so the two entry points can't drift into different behavior."""
    st.session_state.messages.append({"role": "user", "content": question})
    render_message("user", question, newest=True)

    with st.spinner("Searching the handbook..."):
        result = bot.answer_question(question)

    render_message("assistant", result.answer, result.sources, newest=True)
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.answer,
        "sources": result.sources,
    })


# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"], msg.get("sources"), newest=False)

# --- Empty state with clickable suggestions (only before the first message) ---
if not st.session_state.messages:
    render_html(
        """
        <div class="empty-state">
            <div class="empty-state-icon">📘</div>
            <h2>What would you like to know?</h2>
            <p>Ask questions about GitLab's Team Handbook and get answers
            grounded in the indexed documentation, with sources cited.</p>
        </div>
        """
    )

    clicked_suggestion = None
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            with st.container(key=f"suggestion_card_{i}"):
                if st.button(f"💬  {question}", key=f"suggestion_btn_{i}", use_container_width=True):
                    clicked_suggestion = question

    if clicked_suggestion:
        ask(clicked_suggestion)

# --- Chat input ---
user_query = st.chat_input("Ask anything about the GitLab Handbook...")
if user_query:
    ask(user_query)

with st.sidebar:
    if LOGO_URI:
        render_html(
            f"""
            <div class="sidebar-brand">
                <img src="{LOGO_URI}" alt="logo" />
                <div class="sidebar-brand-text">
                    <span class="name">SafeX Handbook Assistant</span>
                    <span class="sub">AI-powered knowledge assistant</span>
                </div>
            </div>
            """
        )

    st.markdown('<div class="sidebar-section-title">About</div>', unsafe_allow_html=True)
    render_html(
        '<div class="sidebar-about">Ask questions about the GitLab Team '
        'Handbook and get grounded answers with source citations.</div>'
    )

    st.markdown('<div class="sidebar-section-title">Built with</div>', unsafe_allow_html=True)
    render_html(
        '<div class="badge-row">'
        '<span class="badge">Python</span>'
        '<span class="badge">LangChain</span>'
        '<span class="badge">ChromaDB</span>'
        '<span class="badge">Gemini</span>'
        '<span class="badge">Streamlit</span>'
        '<span class="badge">RAG</span>'
        '</div>'
    )

    st.markdown('<div class="sidebar-section-title">Status</div>', unsafe_allow_html=True)
    render_html(
        f"""
        <div class="status-card">
            <div class="status-title"><span class="status-dot"></span>Knowledge Base Ready</div>
            <div class="status-sub">{PAGE_COUNT} Handbook Pages Indexed</div>
        </div>
        """
    )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with st.container(key="clear_btn_wrap"):
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    provider = os.getenv("LLM_PROVIDER", "openai")
    st.markdown(
        f'<div class="sidebar-footer">Powered by {provider.capitalize()} + RAG</div>',
        unsafe_allow_html=True,
    )
