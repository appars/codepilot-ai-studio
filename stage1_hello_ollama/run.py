# ============================================================
# CodePilot AI Studio — Stage 1: Hello Ollama
# ============================================================
# Concept  : Talking to a LOCAL Large Language Model (LLM)
# Framework: Ollama + LangChain
# Model    : Mistral (running on your own machine, no internet)
#
# What you will learn:
#   - What Ollama is and why we use it
#   - How LangChain connects Python to a local LLM
#   - How to send a prompt and get a response
#   - The difference between a local LLM and ChatGPT
#
# Run this file:
#   python run.py
#
# Expected output:
#   A response from Mistral explaining what a bug is in code
# ============================================================

# ── IMPORTS ─────────────────────────────────────────────────
# langchain_ollama gives us a clean Python interface to Ollama
# without it, we would have to write raw HTTP requests
from langchain_ollama import OllamaLLM

# ── STEP 1: Choose your model ────────────────────────────────
# Ollama runs the model locally on your machine.
# "mistral" is a 7-billion parameter model — fast and good at code.
# If your laptop has only 4GB RAM, change "mistral" to "phi3:mini"
MODEL_NAME = "mistral"

# ── STEP 2: Create the LLM object ───────────────────────────
# OllamaLLM connects to the Ollama service running on port 11434.
# Make sure Ollama is running before executing this script!
# On Mac:     ollama serve  (in a separate terminal)
# On Windows: Ollama starts automatically as a background service
llm = OllamaLLM(model=MODEL_NAME)

# ── STEP 3: Write a prompt ───────────────────────────────────
# A prompt is simply the instruction/question we send to the model.
# We are asking it to act as a coding assistant.
prompt = """
You are a helpful Python coding assistant.
Explain what a 'bug' is in software in simple terms.
Give one real example of a common Python bug.
Keep your answer under 100 words.
"""

# ── STEP 4: Send the prompt and get a response ───────────────
# llm.invoke() sends the prompt to Mistral and waits for the reply.
# This may take 20-60 seconds the FIRST time (model loads into RAM).
# After the first call, responses are much faster.
print("=" * 60)
print("CodePilot AI Studio — Stage 1: Hello Ollama")
print("=" * 60)
print(f"Model : {MODEL_NAME}")
print(f"Prompt: {prompt.strip()}")
print("-" * 60)
print("Mistral says:")
print()

response = llm.invoke(prompt)  # this is where the magic happens!

print(response)
print("=" * 60)
print("✅ Stage 1 complete! Ollama is working on your machine.")

# ── WHAT JUST HAPPENED? ──────────────────────────────────────
# 1. Python sent your prompt to Ollama via localhost:11434
# 2. Ollama loaded the Mistral model into RAM
# 3. Mistral generated a response token by token
# 4. LangChain returned the full response as a Python string
# No internet was used. Everything ran on YOUR machine.

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Change the prompt — ask it to explain a different concept
# 2. Change MODEL_NAME to "phi3:mini" — notice the speed difference
# 3. Ask it to write a simple Python function — does it work?
# 4. What happens if Ollama is not running? (try stopping it)
