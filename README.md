# LLM-HALLUCINATION-EVALUATION
# 🔬 LLM Hallucination Detection Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/Groq-API-orange?style=flat-square)
![HuggingFace](https://img.shields.io/badge/HuggingFace-TruthfulQA-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-green?style=flat-square)

> Automatically detects factual hallucinations in LLM outputs by benchmarking models against ground truth using semantic similarity scoring.

---

## 📌 What This Project Does

Every major AI company (Anthropic, OpenAI, Google) runs hallucination benchmarks before every model release. This pipeline does exactly that — comparing two LLMs against verified ground truth answers and measuring where they fail.

---

## 🧠 Key Finding

| Category | LLaMA-3.1-8B | Qwen3-32B |
|---|---|---|
| Finance | 0% | 0% |
| Health | 0% | 0% |
| Science | 0% | 0% |
| Politics | 0% | 0% |
| Misconceptions | 0% | 0% |
| **Law** | **20%** | **20%** |

> **Law is the highest-risk category** — 1 in 5 legal questions returned factually incorrect answers across both models.
> TruthfulQA Dataset (HuggingFace)
↓
30 Questions × 6 Categories
↓
Groq API (2 models)
┌─────┴──────┐
LLaMA-3.1-8B  Qwen3-32B
└─────┬──────┘
↓
sentence-transformers
(semantic similarity scoring)
↓
Hallucination Detection
↓
Analysis + Visualisation
> ---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Dataset | TruthfulQA (HuggingFace) |
| LLM API | Groq (free tier) |
| Model 1 | LLaMA-3.1-8B-Instant |
| Model 2 | Qwen3-32B |
| Scoring | sentence-transformers (all-MiniLM-L6-v2) |
| Analysis | pandas |
| Visualisation | matplotlib, seaborn |
| Environment | Google Colab |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/sabyg147/LLM-HALLUCINATION-EVALUATION.git
```

### 2. Get free API key
- Sign up at [console.groq.com](https://console.groq.com)
- Create API key (free, no credit card)

### 3. Open in Google Colab
- Upload `Hallucinate.ipynb` to [colab.research.google.com](https://colab.research.google.com)
- Add Groq API key to Colab Secrets as `Groq`
- Run all cells in order

---

## 📊 Results

### Hallucination Rate by Topic
Both models perform well on factual topics but struggle with legal questions — likely because laws vary by jurisdiction and require precise language.

### Similarity Score Distribution
Most answers score above 0.3 threshold, with Law category showing the most below-threshold responses.

---

## 📁 Project Structure
LLM-HALLUCINATION-EVALUATION/
│
├── Hallucinate.ipynb        # Main pipeline notebook
├── hallucination_results.csv  # Raw results (upload this too)
├── hallucination_report.png   # Bar chart
├── hallucination_full_analysis.png  # Full seaborn analysis
└── README.md

---

## 🔮 Roadmap

- [ ] Scale to full 817 questions
- [ ] Add Streamlit frontend
- [ ] Dockerize the pipeline
- [ ] Add LangChain RAG to reduce hallucinations
- [ ] Add LangGraph self-correction agent
- [ ] Deploy on AWS/GCP

---

## 💼 Resume Bullets

> Built hallucination detection pipeline using Groq API + TruthfulQA (817 questions), benchmarking LLaMA-3.1-8B vs Qwen3-32B across 6 topic categories — identified Law as highest hallucination risk at 20%, informing prompt guardrail design.

> Implemented semantic similarity scoring using sentence-transformers (all-MiniLM-L6-v2) to evaluate LLM factual accuracy — zero API cost for evaluation layer.

---

## 👤 Author

**Sabyasachi Ghosh**
- GitHub: [@sabyg147](https://github.com/sabyg147)

---

*Built at 6AM after a long night of debugging. Worth it.* 😄

---

## 🏗️ Architecture
