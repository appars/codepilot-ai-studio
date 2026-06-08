# Stage 1 — Hello Ollama 🦙

> **Concept:** Talking to a local Large Language Model (LLM) with no internet and no API key.

---

## 1. What You Will Learn

By the end of this stage you will understand:

- What **Ollama** is — a tool that runs AI models on your own laptop
- What **Mistral** is — a powerful open-source LLM that runs locally
- How **LangChain** connects Python code to a local LLM
- The difference between a **local LLM** (this) and **ChatGPT** (cloud)

### The Big Idea

```
Your Python code
      ↓
   LangChain          ← the connector (like a USB cable)
      ↓
    Ollama             ← the engine (runs on your laptop)
      ↓
   Mistral 7B          ← the brain (the actual AI model)
      ↓
   Response            ← back to your Python code
```

**No internet. No API key. No cost. Everything runs on your machine.**

---

## 2. How It Works

### What is Ollama?
Ollama is a free tool that downloads and runs open-source AI models on your laptop.  
Think of it like having a local version of ChatGPT that never sends your data anywhere.

### What is Mistral?
Mistral 7B is an open-source language model with 7 billion parameters.  
It is excellent at understanding and generating code.  
It runs comfortably on a laptop with 8GB RAM.

### What is LangChain?
LangChain is a Python framework that makes it easy to build AI applications.  
In Stage 1 we only use its simplest feature — `OllamaLLM` — to send a prompt and get a reply.  
In later stages we add memory, tools, and workflows on top.

### The flow in code
```
llm = OllamaLLM(model="mistral")   # connect to Ollama
response = llm.invoke("your prompt here")   # send prompt, get reply
print(response)   # show the answer
```
That's it. 3 lines to talk to a local AI.

---

## 3. Setup and Run Commands

### Prerequisites
Make sure these are done **before** running:

**Step 1 — Install Ollama**

On Mac:
```bash
brew install ollama
# OR download from https://ollama.com and install the .dmg
```

On Windows:
```bash
# Download OllamaSetup.exe from https://ollama.com
# Run the installer — Ollama starts automatically as a Windows service
```

**Step 2 — Pull the Mistral model**
```bash
ollama pull mistral
# This downloads ~4GB — do this BEFORE class on your home WiFi!
# If your laptop has only 4GB RAM, use this instead:
ollama pull phi3:mini
```

**Step 3 — Start Ollama**

On Mac (open a new terminal and keep it running):
```bash
ollama serve
```

On Windows:
```bash
# Ollama starts automatically — no action needed
# Verify it is running: open http://localhost:11434 in browser
# You should see: "Ollama is running"
```

**Step 4 — Set up Python environment**

On Mac:
```bash
cd stage1_hello_ollama
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows:
```bash
cd stage1_hello_ollama
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Step 5 — Run!**
```bash
python run.py
```

---

## 4. Expected Output

When everything works, you will see something like this:

```
============================================================
CodePilot AI Studio — Stage 1: Hello Ollama
============================================================
Model : mistral
Prompt: You are a helpful Python coding assistant...
------------------------------------------------------------
Mistral says:

A bug is an error in software that causes it to behave
unexpectedly. For example, a common Python bug is an
IndexError — trying to access list[5] when the list only
has 3 items. This crashes the program because index 5
does not exist.

============================================================
✅ Stage 1 complete! Ollama is working on your machine.
```

**First run is slow** — Mistral takes 30–60 seconds to load into RAM.  
After that, responses are much faster (5–10 seconds).

---

## 5. Code Walkthrough

Let's go through `run.py` line by line:

```python
from langchain_ollama import OllamaLLM
```
This imports the LangChain connector for Ollama.  
Without this, you would need to write raw HTTP requests to `localhost:11434`.

```python
MODEL_NAME = "mistral"
```
We store the model name in a variable so it is easy to change later.  
To use a lighter model on low-RAM laptops: `MODEL_NAME = "phi3:mini"`

```python
llm = OllamaLLM(model=MODEL_NAME)
```
This creates a connection object to Ollama.  
It does NOT send anything yet — it just prepares the connection.

```python
prompt = """ ... """
```
A prompt is the instruction we give to the model.  
Good prompts are specific and tell the model exactly what role to play.

```python
response = llm.invoke(prompt)
```
THIS is where the actual call happens.  
`invoke()` sends the prompt to Ollama, waits for the full response, and returns it as a Python string.

```python
print(response)
```
Simple as that — the response is just a string you can print, store, or process.

---

## 6. Common Errors and Fixes

### ❌ Error: `Connection refused` or `Failed to connect`
**Cause:** Ollama is not running.  
**Fix on Mac:** Open a new terminal and run `ollama serve`  
**Fix on Windows:** Search for "Ollama" in your system tray (bottom right). If missing, restart it from Start Menu.

### ❌ Error: `model "mistral" not found`
**Cause:** You haven't downloaded the model yet.  
**Fix:** Run `ollama pull mistral` in your terminal.

### ❌ Error: `ModuleNotFoundError: No module named 'langchain_ollama'`
**Cause:** Dependencies not installed.  
**Fix:** Make sure your virtual environment is active, then run `pip install -r requirements.txt`

### ❌ The response is very slow (more than 2 minutes)
**Cause:** Your laptop has 4GB RAM and Mistral is too large.  
**Fix:** Change `MODEL_NAME = "mistral"` to `MODEL_NAME = "phi3:mini"` in `run.py`  
Then run: `ollama pull phi3:mini`

### ❌ On Windows: `venv\Scripts\activate` gives an error
**Cause:** PowerShell execution policy is blocking scripts.  
**Fix:** Run this command first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 7. Try It Yourself

Now that it is working, experiment:

**Experiment 1 — Change the prompt**  
Open `run.py` and change the prompt to:
```
"Write a Python function that adds two numbers. Add comments to explain each line."
```
Run it. Does Mistral write good code?

**Experiment 2 — Try a different model**  
Change `MODEL_NAME = "mistral"` to `MODEL_NAME = "phi3:mini"`  
Run it. Is it faster? Is the quality different?

**Experiment 3 — What happens without Ollama?**  
Stop Ollama and run the script again.  
Read the error message carefully — this helps you debug connection issues.

---

## What's Next?

In **Stage 2** we add **memory** — so the agent remembers what you said earlier in the conversation.  
Right now, every `llm.invoke()` call is independent — the model has no idea what you asked before.

➡️ Move to [`../stage2_memory_agent/`](../stage2_memory_agent/README.md)

---

## Key Vocabulary

| Term | Meaning |
|------|---------|
| LLM | Large Language Model — the AI brain (Mistral, GPT-4, etc.) |
| Ollama | Tool that runs LLMs locally on your laptop |
| LangChain | Python framework for building AI applications |
| `invoke()` | LangChain method to send a prompt and get a response |
| Prompt | The instruction or question you send to the model |
| Local inference | Running AI on your own machine, no internet needed |
