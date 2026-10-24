"""Streamlit UI for ResearchMind. Run with: streamlit run app.py"""
import time

import streamlit as st

from pipeline import run_critic, run_reader, run_search, run_writer

st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.stApp { background: #0a0a0f; color: #e8e4dc; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }
.hero { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero h1 { font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 800; color: #f0ebe0; margin: 0; }
.hero h1 span { color: #ff8c32; }
.hero p { color: #a09890; max-width: 520px; margin: .8rem auto 0; }
.step-card { border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
             padding: 1rem 1.3rem; margin-bottom: .9rem; background: rgba(255,255,255,.03); }
.step-card.active { border-color: rgba(255,140,50,.5); background: rgba(255,140,50,.05); }
.step-card.done   { border-color: rgba(80,200,120,.4); background: rgba(80,200,120,.04); }
.step-title { font-weight: 700; color: #f0ebe0; }
.step-desc  { font-size: .82rem; color: #8a8278; }
.step-status{ float: right; font-family: monospace; font-size: .72rem; }
.stButton > button { background: linear-gradient(135deg,#ff8c32,#ff5a1a); color: #0a0a0f;
                     font-weight: 700; border: none; border-radius: 10px; }
</style>
<div class="hero">
  <h1>Research<span>Mind</span></h1>
  <p>Four specialized AI agents collaborate: searching, scraping, writing and
     critiquing, to deliver a research report on any topic.</p>
</div>
""",
    unsafe_allow_html=True,
)

STEPS = [
    ("search", "01 · Search Agent", "Gathers recent web information"),
    ("reader", "02 · Reader Agent", "Scrapes and extracts deep content"),
    ("writer", "03 · Writer Chain", "Drafts the full research report"),
    ("critic", "04 · Critic Chain", "Reviews and scores the report"),
]


def render_steps(placeholder, results: dict, running_key: str | None):
    html = ""
    for key, title, desc in STEPS:
        if key in results:
            cls, label = "done", "✓ DONE"
        elif key == running_key:
            cls, label = "active", "● RUNNING"
        else:
            cls, label = "", "WAITING"
        html += (
            f'<div class="step-card {cls}"><span class="step-status">{label}</span>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div></div>'
        )
    placeholder.markdown(html, unsafe_allow_html=True)


if "results" not in st.session_state:
    st.session_state.results = {}

col_in, col_pipe = st.columns([5, 4], gap="large")

with col_in:
    topic = st.text_input(
        "Research topic", placeholder="e.g. Quantum computing breakthroughs in 2026"
    )
    run_btn = st.button("⚡ Run Research Pipeline", use_container_width=True)

with col_pipe:
    st.subheader("Pipeline")
    steps_box = st.empty()
    render_steps(steps_box, st.session_state.results, None)

if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        results: dict = {}
        st.session_state.results = results
        try:
            render_steps(steps_box, results, "search")
            results["search"] = run_search(topic)

            render_steps(steps_box, results, "reader")
            results["reader"] = run_reader(topic, results["search"])

            render_steps(steps_box, results, "writer")
            results["writer"] = run_writer(topic, results["search"], results["reader"])

            render_steps(steps_box, results, "critic")
            results["critic"] = run_critic(results["writer"])

            render_steps(steps_box, results, None)
        except Exception as e:
            st.error(f"Pipeline failed: {e}")

r = st.session_state.results
if r:
    st.divider()
    if "search" in r:
        with st.expander("🔍 Search results (raw)"):
            st.text(r["search"])
    if "reader" in r:
        with st.expander("📄 Scraped content (raw)"):
            st.text(r["reader"])
    if "writer" in r:
        st.header("📝 Final Research Report")
        st.markdown(r["writer"])
        st.download_button(
            "⬇ Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )
    if "critic" in r:
        st.header("🧐 Critic Feedback")
        st.markdown(r["critic"])
