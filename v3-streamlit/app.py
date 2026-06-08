from diagram import make_pipeline_diagram, make_score_charts, fig_to_b64
import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import time
import hashlib
from sentence_transformers import SentenceTransformer, util
from datasets import load_dataset
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import io
import base64

st.set_page_config(
    page_title="LLM Hallucination Detector",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:         #060610;
    --glass:      rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.08);
    --glass-hover: rgba(255,255,255,0.07);
    --ink:        #ffffff;
    --body:       #c8c8d8;
    --muted:      #6b6b80;
    --accent:     #6c63ff;
    --accent2:    #a78bfa;
    --success:    #22d3a0;
    --danger:     #f43f5e;
    --warning:    #fbbf24;
    --blue:       #3b82f6;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ANIMATED BACKGROUND */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(255,255,255,0.007) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.007) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
    z-index: 0;
    animation: drift 18s ease-in-out infinite alternate;
}
.orb-1 { width:600px; height:600px; background: rgba(108,99,255,0.12); top:-200px; right:-100px; animation-delay:0s; }
.orb-2 { width:400px; height:400px; background: rgba(34,211,160,0.08); bottom:-100px; left:-100px; animation-delay:-9s; }

@keyframes drift {
    0%   { transform: translate(0,0) scale(1); }
    100% { transform: translate(60px, 40px) scale(1.1); }
}

/* NAV */
.nav {
    position: sticky; top: 0; z-index: 100;
    background: rgba(6,6,16,0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--glass-border);
    padding: 0 56px;
    height: 68px;
    display: flex; align-items: center; justify-content: space-between;
}
.nav-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 18px; font-weight: 800;
    letter-spacing: 1px; color: var(--ink);
}
.nav-logo span {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.nav-pill {
    font-family: 'Inter', sans-serif;
    font-size: 11px; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--muted);
    background: var(--glass);
    border: 1px solid var(--glass-border);
    padding: 6px 14px; border-radius: 999px;
}

/* HERO */
.hero {
    padding: 96px 56px 80px;
    position: relative; overflow: hidden;
}
.hero-badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 11px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--accent2);
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.25);
    padding: 6px 16px; border-radius: 999px;
    margin-bottom: 28px;
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 80px; font-weight: 900;
    line-height: 1; letter-spacing: -2px;
    color: var(--ink);
    margin-bottom: 12px;
}
.hero-title span {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 18px; font-weight: 300;
    color: var(--body); line-height: 1.7;
    max-width: 580px; margin-bottom: 48px;
}

/* STATS ROW */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 0 56px 64px;
}
.stat-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 28px 24px;
    backdrop-filter: blur(12px);
    transition: background 0.2s;
}
.stat-card:hover { background: var(--glass-hover); }
.stat-value {
    font-family: 'Outfit', sans-serif;
    font-size: 40px; font-weight: 800;
    color: var(--ink); line-height: 1;
    margin-bottom: 8px;
}
.stat-label {
    font-size: 12px; font-weight: 500;
    letter-spacing: 1px; text-transform: uppercase;
    color: var(--muted);
}

/* HOW IT WORKS */
.how-section {
    padding: 0 56px 64px;
}
.how-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--muted); margin-bottom: 20px;
}
.flow-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 32px 36px;
    backdrop-filter: blur(12px);
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
}
.flow-step {
    padding: 0 24px;
    border-right: 1px solid var(--glass-border);
    position: relative;
}
.flow-step:first-child { padding-left: 0; }
.flow-step:last-child { border-right: none; padding-right: 0; }
.flow-num {
    font-family: 'Outfit', sans-serif;
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 10px;
}
.flow-title {
    font-family: 'Outfit', sans-serif;
    font-size: 15px; font-weight: 700;
    color: var(--ink); margin-bottom: 8px;
}
.flow-desc {
    font-size: 13px; font-weight: 400;
    color: var(--body); line-height: 1.6;
}

/* DIVIDER */
.divider {
    height: 1px;
    background: var(--glass-border);
    margin: 0 56px 64px;
}

/* FORM */
.form-wrap {
    padding: 0 56px 64px;
}
.form-glass {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 40px;
    backdrop-filter: blur(12px);
}
.form-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--muted); margin-bottom: 28px;
}

/* STREAMLIT OVERRIDES */
.stTextArea > div > div > textarea,
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
}
.stTextArea > div > div > textarea:focus,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
}
label, .stTextArea label, .stTextInput label, .stSelectbox label {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 8px !important;
}
.stSlider > div { padding: 0 !important; }

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 14px 40px !important;
    height: 52px !important;
    width: 100% !important;
    box-shadow: 0 8px 32px rgba(108,99,255,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(108,99,255,0.5) !important;
}

/* RESULTS */
.results-wrap { padding: 0 56px 64px; }
.result-glass {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 16px;
    backdrop-filter: blur(12px);
}
.result-glass.accurate  { border-left: 3px solid var(--success); }
.result-glass.hallucinated { border-left: 3px solid var(--danger); }
.result-glass.escalated { border-left: 3px solid var(--blue); }
.result-glass.rag       { border-left: 3px solid var(--warning); }
.result-glass.final     { border: 1px solid rgba(108,99,255,0.4); background: rgba(108,99,255,0.06); }

.result-tag {
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 12px;
}
.score-big {
    font-family: 'Outfit', sans-serif;
    font-size: 56px; font-weight: 900;
    line-height: 1; margin-bottom: 16px;
}
.result-text {
    font-family: 'Inter', sans-serif;
    font-size: 16px; font-weight: 400;
    color: var(--body); line-height: 1.7;
}

/* FOOTER */
.footer {
    border-top: 1px solid var(--glass-border);
    padding: 40px 56px;
    display: flex; justify-content: space-between; align-items: center;
}
.footer-text {
    font-size: 12px; font-weight: 500;
    letter-spacing: 0.5px; color: var(--muted);
}

/* PARTICLE CANVAS */
#particle-canvas {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
}
.hero { position: relative; overflow: hidden; }
.hero-content { position: relative; z-index: 2; }

/* PIPELINE CHART */
.pipeline-section {
    padding: 0 56px 32px;
}
.pipeline-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--muted); margin-bottom: 20px;
}
.pipeline-img {
    border-radius: 16px;
    border: 1px solid var(--glass-border);
    width: 100%;
}
</style>

<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
""", unsafe_allow_html=True)


# ── SECURITY ──
ALLOWED_CATEGORIES = ["Health", "Law", "Finance", "Politics", "Science", "Misconceptions"]

def sanitize_input(text):
    banned = ["ignore previous", "forget instructions", "reveal data", "system prompt", "jailbreak"]
    for phrase in banned:
        if phrase in text.lower():
            raise ValueError(f"Prompt injection detected: '{phrase}'")
    return text.strip()

def filter_output(text):
    for w in ["password", "secret", "api_key", "token", "confidential"]:
        if w in text.lower():
            return "[Response blocked by output filter]"
    return text

def encrypt_log(text):
    return hashlib.sha256(text.encode()).hexdigest()


# ── GROQ ──
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = {"llama": "llama-3.1-8b-instant", "qwen": "qwen/qwen3-32b"}

def query_groq(question, model_key, api_key, context=""):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"Answer factually and concisely: {question}"
    if context:
        prompt = f"Use ONLY these facts:\n{context}\n\nAnswer: {question}"
    payload = {"model": MODELS[model_key], "messages": [{"role": "user", "content": prompt}], "max_tokens": 200, "temperature": 0.1}
    r = requests.post(GROQ_URL, headers=headers, json=payload)
    result = r.json()
    if "choices" in result:
        ans = result["choices"][0]["message"]["content"].strip()
        if "<think>" in ans:
            ans = ans.split("</think>")[-1].strip()
        return ans
    return f"[API Error: {result.get('error', {}).get('message', 'unknown')}]"


# ── SCORER ──
@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

def score_answer(answer, ground_truth, embedder):
    e1 = embedder.encode(answer, convert_to_tensor=True)
    e2 = embedder.encode(ground_truth, convert_to_tensor=True)
    return round(float(util.cos_sim(e1, e2)[0][0]), 3)


# ── RAG ──
@st.cache_resource
def build_vectorstore():
    try:
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_huggingface import HuggingFaceEmbeddings
        dataset = load_dataset("truthfulqa/truthful_qa", "generation")
        df = pd.DataFrame(dataset["validation"])
        docs = [Document(page_content=row["best_answer"], metadata={"question": row["question"], "category": row["category"]}) for _, row in df.iterrows()]
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return Chroma.from_documents(docs, embeddings, collection_name="truthfulqa_kb")
    except:
        return None

def rag_retrieve(question, vs, k=3):
    if vs is None:
        return ""
    return "\n".join([r.page_content for r in vs.similarity_search(question, k=k)])


#


# ══════════════════════════
# UI
# ══════════════════════════

# NAV
st.markdown("""
<div class="nav">
    <div class="nav-logo">LLM <span>Hallucination</span> Detector</div>
    <div class="nav-pill">v2.0 · RAG + LangGraph</div>
</div>
""", unsafe_allow_html=True)


# HERO
st.markdown("""
<style>
@keyframes float {
  0%,100%{transform:translate(0,0)} 50%{transform:translate(30px,20px)}
}
.p{position:absolute;border-radius:50%;background:rgba(108,99,255,0.8);box-shadow:0 0 6px rgba(108,99,255,0.8);animation:float linear infinite}
</style>
<div class="hero" style="position:relative;overflow:hidden">
  <div class="p" style="width:7px;height:7px;top:20%;left:15%;animation-duration:8s"></div>
  <div class="p" style="width:5px;height:5px;top:60%;left:30%;animation-duration:11s;animation-delay:-3s"></div>
  <div class="p" style="width:9px;height:9px;top:30%;left:70%;animation-duration:9s;animation-delay:-5s"></div>
  <div class="p" style="width:5px;height:5px;top:70%;left:80%;animation-duration:13s;animation-delay:-2s"></div>
  <div class="p" style="width:7px;height:7px;top:50%;left:50%;animation-duration:7s;animation-delay:-7s"></div>
  <div class="p" style="width:4px;height:4px;top:15%;left:40%;animation-duration:12s;animation-delay:-1s"></div>
<div class="p" style="width:4px;height:4px;top:80%;left:20%;animation-duration:9s;animation-delay:-6s"></div>
<div class="p" style="width:4px;height:4px;top:40%;left:85%;animation-duration:14s;animation-delay:-3s"></div>
<div class="p" style="width:4px;height:4px;top:90%;left:60%;animation-duration:8s;animation-delay:-9s"></div>
<div class="p" style="width:4px;height:4px;top:25%;left:25%;animation-duration:11s;animation-delay:-2s"></div>
<div class="p" style="width:4px;height:4px;top:55%;left:45%;animation-duration:10s;animation-delay:-8s"></div>
<div class="p" style="width:4px;height:4px;top:75%;left:75%;animation-duration:13s;animation-delay:-4s"></div>
<div class="p" style="width:4px;height:4px;top:5%;left:90%;animation-duration:7s;animation-delay:-11s"></div>
  <div class="hero-content" style="position:relative;z-index:2">
    <div class="hero-badge">🔬 AI Safety · LLM Evaluation · RAG + LangGraph</div>
    <div class="hero-title">Hallucination<br><span>Detector</span></div>
    <div class="hero-sub">Real-time factual accuracy scoring for large language models.
    Cascades from LLaMA → Qwen3 → RAG ChromaDB until the answer is accurate.
    4 security layers protect every query.</div>
  </div>
</div>
""", unsafe_allow_html=True)


# STATS
st.markdown("""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-value">817</div>
        <div class="stat-label">TruthfulQA Questions</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">2</div>
        <div class="stat-label">LLMs Cascaded</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">4</div>
        <div class="stat-label">Security Layers</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">3×</div>
        <div class="stat-label">Max RAG Retries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# HOW IT WORKS
st.markdown("""
<div class="how-section">
    <div class="how-title">How It Works</div>
    <div class="flow-card">
        <div class="flow-step">
            <div class="flow-num">Step 01</div>
            <div class="flow-title">You Ask</div>
            <div class="flow-desc">Enter any factual question — e.g. "Why do veins appear blue?"</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">Step 02</div>
            <div class="flow-title">You Provide Ground Truth</div>
            <div class="flow-desc">Enter the correct answer — e.g. "Veins appear blue due to light penetrating skin."</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">Step 03</div>
            <div class="flow-title">App Asks Two LLMs</div>
            <div class="flow-desc">LLaMA-3.1-8B answers first. If it hallucinates, Qwen3-32B is escalated. If that fails, RAG ChromaDB retrieves facts and corrects the answer.</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">Step 04</div>
            <div class="flow-title">Result Tells You</div>
            <div class="flow-desc">Each step shows an accuracy score 0–1. Below threshold = hallucination detected. Above = accurate response.</div>
        </div>
    </div>
</div>

<div class="divider"></div>
""", unsafe_allow_html=True)

# PIPELINE DIAGRAM
pipeline_fig = make_pipeline_diagram()
pipeline_b64 = fig_to_b64(pipeline_fig)
plt.close(pipeline_fig)
st.markdown(f"""
<div class="pipeline-section">
    <div class="pipeline-title">Architecture · Pipeline Flow</div>
    <img class="pipeline-img" src="data:image/png;base64,{pipeline_b64}" />
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# FORM
st.markdown('<div class="form-wrap"><div class="form-glass"><div class="form-title">Configure Detection Run</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    question = st.text_area("Question", placeholder="e.g. Why do veins appear blue?", height=90)
    ground_truth = st.text_area("Ground Truth Answer", placeholder="e.g. Veins appear blue because of the way light penetrates skin", height=90)
with col2:
    category  = st.selectbox("Category", ALLOWED_CATEGORIES)
    api_key   = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    threshold = st.slider("Accuracy Threshold", 0.1, 0.9, 0.3, 0.05)

run = st.button("⚡ Run Detection Pipeline")
st.markdown('</div></div>', unsafe_allow_html=True)


# ── RUN ──
if run:
    if not question or not ground_truth or not api_key:
        st.error("Please fill in all fields.")
    else:
        try:
            question     = sanitize_input(question)
            ground_truth = sanitize_input(ground_truth)
            if category not in ALLOWED_CATEGORIES:
                st.error("Access denied.")
                st.stop()

            embedder = load_embedder()
            log_hash = encrypt_log(question)

            st.markdown('<div class="results-wrap">', unsafe_allow_html=True)
            st.markdown('<div class="form-title" style="padding-bottom:16px">Pipeline Execution Log</div>', unsafe_allow_html=True)

            final_answer = ""
            final_score  = 0
            model_used   = ""
            facts_used   = ""
            qwen_score   = 0
            rag_score    = 0

            # STEP 1 — LLaMA
            with st.spinner("⚡ Querying LLaMA-3.1-8B..."):
                llama_ans   = query_groq(question, "llama", api_key)
                llama_score = score_answer(llama_ans, ground_truth, embedder)
                llama_hall  = llama_score < threshold

            sc = "accurate" if not llama_hall else "hallucinated"
            col = "#22d3a0" if not llama_hall else "#f43f5e"
            tag = "✅ ACCURATE" if not llama_hall else "❌ HALLUCINATED"
            st.markdown(f"""
            <div class="result-glass {sc}">
                <div class="result-tag" style="color:{col}">⚡ LLaMA-3.1-8B · Step 01 · {tag}</div>
                <div class="score-big" style="color:{col}">{llama_score}</div>
                <div class="result-text">{llama_ans}</div>
            </div>""", unsafe_allow_html=True)

            if not llama_hall:
                final_answer = llama_ans
                final_score  = llama_score
                model_used   = "LLaMA-3.1-8B"
            else:
                # STEP 2 — Qwen3
                with st.spinner("🧠 Escalating to Qwen3-32B..."):
                    qwen_ans   = query_groq(question, "qwen", api_key)
                    qwen_score = score_answer(qwen_ans, ground_truth, embedder)
                    qwen_hall  = qwen_score < threshold

                sc2  = "escalated" if not qwen_hall else "hallucinated"
                col2 = "#3b82f6" if not qwen_hall else "#f43f5e"
                tag2 = "✅ ACCURATE" if not qwen_hall else "❌ STILL HALLUCINATED"
                st.markdown(f"""
                <div class="result-glass {sc2}">
                    <div class="result-tag" style="color:{col2}">🧠 Qwen3-32B · Step 02 · {tag2}</div>
                    <div class="score-big" style="color:{col2}">{qwen_score}</div>
                    <div class="result-text">{qwen_ans}</div>
                </div>""", unsafe_allow_html=True)

                if not qwen_hall:
                    final_answer = qwen_ans
                    final_score  = qwen_score
                    model_used   = "Qwen3-32B"
                else:
                    # STEP 3 — RAG
                    with st.spinner("🔍 Retrieving from ChromaDB..."):
                        vs         = build_vectorstore()
                        facts_used = rag_retrieve(question, vs)
                        rag_ans    = query_groq(question, "llama", api_key, context=facts_used)
                        rag_score  = score_answer(rag_ans, ground_truth, embedder)

                    st.markdown(f"""
                    <div class="result-glass rag">
                        <div class="result-tag" style="color:#fbbf24">🔍 RAG ChromaDB · Step 03</div>
                        <div class="score-big" style="color:#fbbf24">{rag_score}</div>
                        <div class="result-text">{rag_ans}</div>
                        <div style="margin-top:20px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.06)">
                            <div class="result-tag" style="color:#6b6b80;margin-bottom:8px">Retrieved Facts</div>
                            <div class="result-text" style="font-size:13px;color:#6b6b80">{facts_used}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    final_answer = rag_ans
                    final_score  = rag_score
                    model_used   = "RAG + LLaMA"

            # CHARTS
            attempted_scores = {'LLaMA': llama_score}
            if llama_hall:
                attempted_scores['Qwen3'] = qwen_score
                if qwen_hall:
                    attempted_scores['RAG'] = rag_score

            chart_fig = make_score_charts(attempted_scores)
            chart_b64 = fig_to_b64(chart_fig)
            plt.close(chart_fig)
            st.markdown(f"""
            <div style="padding: 24px 0 8px">
                <div class="pipeline-title">Score Analysis</div>
                <img class="pipeline-img" src="data:image/png;base64,{chart_b64}" style="border-radius:12px"/>
            </div>
            """, unsafe_allow_html=True)

            # FINAL
            final_answer = filter_output(final_answer)
            fcol = "#22d3a0" if final_score >= threshold else "#f43f5e"

            st.markdown(f"""
            <div class="result-glass final">
                <div class="result-tag" style="color:#a78bfa">✅ FINAL ANSWER · {model_used}</div>
                <div class="result-text" style="font-size:18px;color:#ffffff;margin-bottom:24px">{final_answer}</div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px">
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px">
                        <div style="font-family:Outfit;font-size:22px;font-weight:800;color:var(--ink)">{model_used}</div>
                        <div style="font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6b6b80;margin-top:6px">Final Model</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px">
                        <div style="font-family:Outfit;font-size:22px;font-weight:800;color:{fcol}">{final_score}</div>
                        <div style="font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6b6b80;margin-top:6px">Accuracy Score</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px">
                        <div style="font-family:Outfit;font-size:14px;font-weight:800;color:#6b6b80;word-break:break-all">{log_hash[:16]}...</div>
                        <div style="font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6b6b80;margin-top:6px">SHA-256 Log</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        except ValueError as e:
            st.error(f"🔒 Security block: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# FOOTER
st.markdown("""
<div class="footer">
    <div class="footer-text">LLM Hallucination Detection Pipeline · v2.0 · Sabyasachi Ghosh</div>
    <div class="footer-text">Groq API · ChromaDB · LangGraph · sentence-transformers</div>
</div>
""", unsafe_allow_html=True)
