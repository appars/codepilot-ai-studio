# 🤖 CodePilot AI Studio

> **Local-first Agentic AI Engineering Assistant**  
> Built with Streamlit + LangChain + LangGraph + Ollama + ChromaDB  
> No internet. No API key. Runs entirely on your laptop.

---

## What Is This?

CodePilot AI Studio is a hands-on teaching project for **Agentic AI in Software Engineering (Module 4)**.

It teaches every syllabus concept by building a real working application — stage by stage.  
Each stage adds one new capability and maps directly to one syllabus topic.

**By the end, students have built a complete AI coding assistant from scratch.**

---

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/codepilot-ai-studio.git
cd codepilot-ai-studio

# 2. Verify setup (run ONCE to check everything is installed)
python setup_check.py

# 3. Start with Stage 1
cd stage1_hello_ollama
python run.py
```

See [SETUP_MAC.md](SETUP_MAC.md) or [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for full installation instructions.

---

## Learning Path

| Stage | Concept | Time | Key File |
|-------|---------|------|----------|
| [Stage 1](stage1_hello_ollama/) | Local LLM with Ollama | 15 min | `run.py` (~30 lines) |
| [Stage 2](stage2_memory_agent/) | Short-term memory | 20 min | `run.py` (~70 lines) |
| [Stage 3](stage3_tool_agent/) | Tool orchestration | 25 min | `run.py` (~80 lines) |
| [Stage 4](stage4_rag_explain/) | RAG + long-term memory | 30 min | `run.py` (~80 lines) |
| [Stage 5](stage5_reflection_review/) | Reflection + self-improvement | 30 min | `run.py` (~80 lines) |
| [Stage 6](stage6_langgraph_workflow/) | LangGraph + multi-agent | 35 min | `run.py` (~80 lines) |
| [Final App](app_final/) | Complete CodePilot Studio | — | `app.py` |

**In-class target:** Stages 1–3 (everyone) · Stage 4 (fast finishers) · Stages 5–6 (homework)

---

## Syllabus Coverage

| Syllabus Topic | Covered In |
|---------------|------------|
| Short-term memory | Stage 2 |
| Long-term memory | Stage 4 (ChromaDB RAG) |
| Reflection loops & self-improvement | Stage 5 |
| Tool orchestration | Stage 3 |
| LangChain | Stages 2–5 |
| LangGraph | Stage 6 |
| AutoGen (simulated) | Stage 6 |
| Enhancing agents with Generative AI | All stages (Mistral) |

**Lab requirement:** "Build a code assistant or debugging agent" → ✅ This IS the lab.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| UI | Streamlit | Browser-based interface |
| LLM | Ollama + Mistral 7B | Local inference, no cloud |
| Framework | LangChain | Agent chains and memory |
| Workflow | LangGraph | Stateful graph execution |
| Vector DB | ChromaDB | Long-term memory / RAG |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Text-to-vector conversion |
| Language | Python 3.11 | Everything |

**100% local. 100% free. 100% offline after setup.**

---

## Every Stage Contains

```
stageN_name/
├── run.py              # working code, under 80 lines
├── README.md           # 7-section detailed guide
└── requirements.txt    # exact package versions
```

**Code commenting standard:**
- File header block explaining the concept
- Section dividers for every logical step  
- Inline `# WHY` comments on every non-obvious line
- `# TRY THIS` section at the bottom with experiments

**README standard:**
1. What you will learn
2. How it works (with diagram)
3. Setup and run commands
4. Expected output
5. Line-by-line code walkthrough
6. Common errors and fixes
7. Try it yourself experiments

---

## Pre-Class Setup

```bash
# Night before class — run at home on WiFi
python preload.py       # downloads Mistral (~4GB) + embeddings (~90MB)

# Morning of class — verify everything
python setup_check.py   # should show 8/8 ✅
```

---

## Repo Structure

```
codepilot-ai-studio/
├── README.md                       ← this file
├── SETUP_MAC.md                    ← Mac setup (instructor)
├── SETUP_WINDOWS.md                ← Windows setup (students)
├── demo_script.md                  ← minute-by-minute teaching guide
├── preload.py                      ← download models before class
├── setup_check.py                  ← verify everything works
│
├── stage1_hello_ollama/            ← Concept: local LLM
├── stage2_memory_agent/            ← Concept: short-term memory
├── stage3_tool_agent/              ← Concept: tool orchestration
├── stage4_rag_explain/             ← Concept: RAG + long-term memory
├── stage5_reflection_review/       ← Concept: reflection loops
├── stage6_langgraph_workflow/      ← Concept: LangGraph + multi-agent
│
├── app_final/                      ← Complete CodePilot Streamlit app
│   ├── app.py
│   └── requirements.txt
│
└── sample_code/
    └── buggy_sample.py             ← Test code with intentional bugs
```

---

## Instructor Notes

See [demo_script.md](demo_script.md) for the complete 3-hour session plan with:
- Exact timings for each section
- What to say at each stage
- Questions to ask the class
- Emergency fallbacks

---

## Credits

Built for **Agentic AI Software Development — Module 4**  
**Prof. Apparsamy Perumal** · Department of Computer Science & Engineering · Semester 5

Tech: [Ollama](https://ollama.com) · [LangChain](https://langchain.com) · [LangGraph](https://langchain-ai.github.io/langgraph/) · [Streamlit](https://streamlit.io) · [ChromaDB](https://www.trychroma.com) · [HuggingFace](https://huggingface.co)
