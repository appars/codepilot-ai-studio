# SETUP_WINDOWS.md — Windows Student Setup Guide 🪟

> For **5th Semester Students** — complete setup before class day.

---

## ⚠️ Do This The Night Before Class

This setup takes 20–40 minutes. Do it at home on WiFi, not in class.

---

## Quick Reference

```
1. Install Ollama → https://ollama.com → download OllamaSetup.exe
2. Install Python 3.11 → https://python.org → check "Add to PATH"
3. Open Command Prompt as normal user (not Admin)
4. Run the commands below
```

```cmd
ollama pull mistral

git clone https://github.com/YOUR_USERNAME/codepilot-ai-studio.git
cd codepilot-ai-studio
python -m venv venv
venv\Scripts\activate
pip install -r app_final\requirements.txt
python preload.py
python setup_check.py
```

---

## Full Setup Step by Step

### Step 1 — Install Ollama

1. Open your browser and go to: **https://ollama.com**
2. Click **Download** → Download for Windows
3. Run `OllamaSetup.exe`
4. Click through the installer (no special options needed)
5. Ollama starts automatically as a **Windows service** — you do NOT need to start it manually

**Verify Ollama is running:**  
Open your browser and go to: `http://localhost:11434`  
You should see: `Ollama is running`

---

### Step 2 — Download the Mistral Model

1. Press `Windows + R`, type `cmd`, press Enter to open Command Prompt
2. Type this command and press Enter:

```cmd
ollama pull mistral
```

⚠️ This downloads **~4 GB**. Takes 10–30 minutes on home WiFi.  
Do NOT do this in class — it will be very slow on college WiFi.

Also download the lightweight fallback model:
```cmd
ollama pull phi3:mini
```

---

### Step 3 — Install Python 3.11

1. Go to: **https://www.python.org/downloads/**
2. Download **Python 3.11.x** (not 3.12 or 3.13)
3. Run the installer
4. ⚠️ **IMPORTANT: Check the box that says "Add Python to PATH"** before clicking Install
5. Click Install Now

**Verify Python installed correctly:**
```cmd
python --version
```
Should show: `Python 3.11.x`

If you see `python is not recognized`, Python was not added to PATH.  
Fix: Uninstall Python and reinstall with the PATH checkbox checked.

---

### Step 4 — Install Git

1. Go to: **https://git-scm.com/download/win**
2. Download and run the installer (all default options are fine)

**Verify:**
```cmd
git --version
```

---

### Step 5 — Clone the Repository

```cmd
cd C:\
git clone https://github.com/YOUR_USERNAME/codepilot-ai-studio.git
cd codepilot-ai-studio
```

⚠️ **Avoid paths with spaces** — use `C:\codepilot-ai-studio`, not `C:\My Documents\...`

---

### Step 6 — Create Virtual Environment

```cmd
python -m venv venv
```

**Activate the virtual environment:**
```cmd
venv\Scripts\activate
```

Your prompt should now start with `(venv)`:
```
(venv) C:\codepilot-ai-studio>
```

If you get a **PowerShell error** about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try `venv\Scripts\activate` again.

---

### Step 7 — Install Python Packages

Make sure `(venv)` is showing in your prompt, then:
```cmd
pip install -r app_final\requirements.txt
```

This installs all required libraries. Takes 3–5 minutes.

---

### Step 8 — Download Embeddings

```cmd
python preload.py
```

This downloads the HuggingFace embedding model (~90MB).  
After this, no internet is needed.

---

### Step 9 — Verify Everything Works

```cmd
python setup_check.py
```

**Expected output:**
```
✅ Python version: 3.11.x
✅ streamlit: installed
✅ langchain: installed
... (all packages)
✅ Ollama service: running on port 11434
✅ Mistral model: available
✅ HuggingFace embeddings: working
✅ Ollama LLM response: responding
✅ ChromaDB read/write: working

🎉 Everything is working! You are ready for class.
```

If any check fails, see the Troubleshooting section below.

---

## On Class Day

Open Command Prompt and run:
```cmd
cd C:\codepilot-ai-studio

venv\Scripts\activate

cd stage1_hello_ollama
python run.py
```

That's it! Follow Prof. Appar's instructions from there.

---

## RAM — Which Model to Use?

| Your RAM | Use this model | Change in code |
|----------|---------------|----------------|
| 8GB or more | `mistral` | Default — no change needed |
| 4–6GB | `phi3:mini` | Change `MODEL_NAME = "phi3:mini"` in `run.py` |

**Check your RAM:**  
Press `Windows + R` → type `dxdiag` → see "Memory" line

---

## Troubleshooting

### ❌ `python` not found / `python is not recognized`
**Cause:** Python not added to PATH during install.  
**Fix:** Uninstall Python from Control Panel. Reinstall from python.org — this time check "Add Python to PATH" ✓

### ❌ `venv\Scripts\activate` gives error about execution policy
**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then activate again.

### ❌ Ollama pull fails / very slow
**Cause:** Slow internet or no internet.  
**Fix:** Do this at home before class. The model is ~4GB.

### ❌ `pip install` fails with SSL error
**Fix:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r app_final\requirements.txt
```

### ❌ First response takes 60+ seconds
**Cause:** Mistral loading into RAM for the first time.  
**This is normal!** Subsequent responses are 10–20 seconds.  
If your laptop has only 4GB RAM, switch to phi3:mini.

### ❌ ChromaDB error with paths on Windows
**Cause:** Path contains spaces or special characters.  
**Fix:** Make sure you cloned to `C:\codepilot-ai-studio` (no spaces in path).

### ❌ `ModuleNotFoundError` for any package
**Cause:** Virtual environment not active.  
**Fix:** Always activate venv first: `venv\Scripts\activate`  
You must do this every time you open a new Command Prompt.

---

## Getting Help

If stuck, check this in order:
1. Is Ollama running? → open `http://localhost:11434` in browser
2. Is venv active? → look for `(venv)` in prompt
3. Run `python setup_check.py` → it tells you exactly what's wrong
4. Ask Prof. Appar or a classmate who got it working
