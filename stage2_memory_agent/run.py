# ============================================================
# CodePilot AI Studio — Stage 2: Memory Agent
# ============================================================
# Concept  : Short-term memory using ConversationBufferMemory
# Framework: LangChain + Ollama
# Model    : Mistral (local)
#
# What you will learn:
#   - Why an AI agent needs memory
#   - What short-term (conversation) memory is
#   - How ConversationBufferMemory stores chat history
#   - How a PromptTemplate injects memory into every prompt
#   - The difference between a stateless LLM and a memory agent
#
# The problem we are solving:
#   Without memory, every llm.invoke() call is independent.
#   The agent forgets everything after each response.
#   With memory, the agent remembers the full conversation.
#
# Run this file:
#   python run.py
#
# Expected output:
#   A multi-turn conversation where the agent recalls context
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
from langchain_ollama import OllamaLLM                    # local LLM connection
from langchain.memory import ConversationBufferMemory     # stores chat history
from langchain.chains import ConversationChain            # chains LLM + memory together
from langchain.prompts import PromptTemplate              # formats our prompt with memory

# ── STEP 1: Connect to the local LLM ─────────────────────────
# Same as Stage 1 — connect to Mistral running in Ollama
# temperature=0.7 controls creativity: 0=robotic, 1=very creative
llm = OllamaLLM(
    model="mistral",      # the local model to use
    temperature=0.7       # balanced between creative and precise
)

# ── STEP 2: Create short-term memory ─────────────────────────
# ConversationBufferMemory stores ALL messages in a list.
# Think of it like a notepad the agent reads before every reply.
#
# memory_key="chat_history"
#   → the variable name used inside the prompt template below
#   → MUST match the {chat_history} placeholder in the prompt
#
# return_messages=True
#   → stores messages as structured objects (HumanMessage, AIMessage)
#   → this makes it easier to process history later
memory = ConversationBufferMemory(
    memory_key="chat_history",   # must match prompt template variable
    return_messages=True          # store as message objects, not raw text
)

# ── STEP 3: Define the prompt template ───────────────────────
# A PromptTemplate is a reusable prompt with placeholder variables.
# Every time the agent is called, LangChain fills in:
#   {chat_history} → the full conversation so far (from memory)
#   {input}        → the user's latest message
#
# The agent sees the FULL conversation before generating each reply.
# This is how it "remembers" — it re-reads the history every time.
prompt_template = PromptTemplate(
    input_variables=["chat_history", "input"],  # variables to fill in
    template="""You are CodePilot, a helpful Python coding assistant.
You remember everything from our conversation so far.

Conversation so far:
{chat_history}

Student: {input}
CodePilot:"""
)

# ── STEP 4: Create the conversation chain ────────────────────
# ConversationChain wires together three components:
#   llm     → the brain (Mistral)
#   memory  → the notepad (ConversationBufferMemory)
#   prompt  → the template that formats everything
#
# When you call chain.predict(input="..."):
#   1. memory loads previous messages into {chat_history}
#   2. prompt template combines history + new input
#   3. llm generates a response
#   4. memory saves the new exchange automatically
chain = ConversationChain(
    llm=llm,                    # our local Mistral model
    memory=memory,              # short-term memory store
    prompt=prompt_template,     # how to format the full prompt
    verbose=False               # set True to see the full prompt sent to LLM
)

# ── STEP 5: Run a multi-turn conversation ────────────────────
# We simulate a student asking follow-up questions.
# Notice how later questions reference earlier answers — proof memory works!

print("=" * 60)
print("CodePilot AI Studio — Stage 2: Memory Agent")
print("=" * 60)
print("Demonstrating short-term memory across multiple turns...")
print()

# --- Turn 1: Ask a general question ---
question1 = "What is an IndexError in Python?"
print(f"👤 Student: {question1}")
response1 = chain.predict(input=question1)  # memory is empty on first call
print(f"🤖 CodePilot: {response1}")
print()

# --- Turn 2: Ask a follow-up that needs context from Turn 1 ---
# The agent must remember "IndexError" was discussed to answer this well
question2 = "Can you give me a simple code example of that error?"
print(f"👤 Student: {question2}")
response2 = chain.predict(input=question2)  # memory now has Turn 1
print(f"🤖 CodePilot: {response2}")
print()

# --- Turn 3: Another follow-up — even deeper context needed ---
# "Fix the bug you just showed" only makes sense with memory
question3 = "How do I fix the bug you just showed me?"
print(f"👤 Student: {question3}")
response3 = chain.predict(input=question3)  # memory has Turns 1 and 2
print(f"🤖 CodePilot: {response3}")
print()

# ── STEP 6: Inspect the memory contents ─────────────────────
# Let's peek inside the memory to see what was stored.
# This is great for understanding HOW memory works under the hood.
print("-" * 60)
print("📦 What is stored in memory right now?")
print("-" * 60)
stored_messages = memory.chat_memory.messages  # list of all messages
for i, msg in enumerate(stored_messages):
    # Each message has a type (Human or AI) and content
    msg_type = "👤 Student" if "Human" in type(msg).__name__ else "🤖 CodePilot"
    print(f"[{i+1}] {msg_type}: {msg.content[:80]}...")  # show first 80 chars
print()
print(f"Total messages in memory: {len(stored_messages)}")
print("=" * 60)
print("✅ Stage 2 complete! Memory is working.")
print()
print("KEY INSIGHT: The agent sees ALL past messages before every reply.")
print("This is short-term memory — it lives only while the program runs.")
print("When you restart the script, memory is gone. Stage 4 fixes that!")

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Set verbose=True in ConversationChain — see the full prompt sent to LLM
# 2. Add a 4th question: "What was my very first question?" — does it remember?
# 3. Change return_messages=False — how does the output change?
# 4. What happens if you ask something completely unrelated to coding?
#    Does the agent still remember the earlier coding questions?
