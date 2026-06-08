# SETUP_MAC.md — MacBook Pro Setup Guide 🍎

> For **Prof. Apparsamy Perumal** — demo machine setup before class day.

---

## Quick Reference

```bash
# One-time setup (do this at home)
brew install ollama python@3.11
ollama pull mistral
ollama pull phi3:mini

cd codepilot-ai-studio
python3 -m venv venv
source venv/bin/activate
pip install -r app_final/requirements.txt
python preload.py       # downloads embeddings

# Verify everything works
python setup_check.py

# On class day — run this first to warm up the model
ollama serve            # keep this terminal open!
cd app_final
streamlit run app.py    # opens browser at http://localhost:8501
```

---

## Full Setup (First Time Only)

### Step 1 — Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2 — Install Ollama
```bash
brew install ollama
# OR download the .dmg from https://ollama.com
```

### Step 3 — Install Python 3.11
```bash
brew install python@3.11
python3 --version    # should show 3.11.x
```

### Step 4 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/codepilot-ai-studio.git
cd codepilot-ai-studio
```

### Step 5 — Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
# Prompt changes to: (venv) $
```

### Step 6 — Install all dependencies
```bash
pip install -r app_final/requirements.txt
```

### Step 7 — Download models and embeddings
```bash
# Start Ollama first (in a separate terminal — keep it open)
ollama serve

# In your main terminal (with venv active):
python preload.py
# Takes 10-30 minutes — do this at home on fast WiFi!
```

### Step 8 — Verify everything works
```bash
python setup_check.py
# Should show: 8/8 checks passed ✅
```

---

## Apple Silicon Notes (M1/M2/M3)

Your MacBook Pro runs Mistral **significantly faster** than student Windows laptops.

| Machine | First response | Subsequent responses |
|---------|---------------|---------------------|
| MacBook Pro M2 | 5-10 seconds | 2-5 seconds |
| Student Windows i5 8GB | 30-60 seconds | 10-20 seconds |

**Important for demo day:** Warn students that their first response will be slow (model loading into RAM). This is normal — not a bug.

---

## Demo Day Checklist (Morning of Class)

Run these the morning of your session:

```bash
# 1. Start Ollama (keep this terminal open all day)
ollama serve

# 2. Activate your virtual environment
cd codepilot-ai-studio
source venv/bin/activate

# 3. Verify everything still works
python setup_check.py

# 4. Warm up the model (so first demo is not slow)
python -c "from langchain_ollama import OllamaLLM; llm = OllamaLLM(model='mistral'); print(llm.invoke('Say: ready'))"

# 5. Start the final app
cd app_final
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Class Day Stage Flow

### Block 1 (0:00–0:40) — Concept Slides
No terminal needed. Just your slides.

### Block 2 (0:40–1:15) — Live Demo
```bash
# Keep ollama serve running in Terminal 1

# Terminal 2 — run each stage
cd stage1_hello_ollama && python run.py    # ~2 min
cd ../stage2_memory_agent && python run.py # ~3 min
cd ../stage3_tool_agent && python run.py   # ~4 min

# Show final app — the "wow" moment
cd ../app_final && streamlit run app.py
```

### Block 3 (1:15–3:00) — Students hands-on
You circulate helping. Keep your terminal ready to debug student issues.

---

## Troubleshooting

### Ollama won't start
```bash
# Kill any stuck Ollama processes
pkill ollama
# Wait 5 seconds, then restart
ollama serve
```

### Port 11434 already in use
```bash
lsof -i :11434          # see what's using it
kill -9 <PID>           # kill it
ollama serve            # restart
```

### Virtual environment not activating
```bash
# Make sure you're in the repo root
pwd   # should show .../codepilot-ai-studio
source venv/bin/activate
```

### Streamlit port already in use
```bash
streamlit run app.py --server.port 8502
# Then open http://localhost:8502
```

### Slow responses during demo
Mistral is loaded into RAM — subsequent calls are fast. If the first call takes >60 seconds, you may have another process using RAM. Close other apps before the demo.
