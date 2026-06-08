# Stage 3 — Tool Agent 🔧

> **Concept:** Tool Orchestration — the agent detects intent and routes to the right specialised skill automatically.

---

## 1. What You Will Learn

By the end of this stage you will understand:

- What **tool orchestration** means in agentic AI
- Why **specialised prompts** produce better results than one generic prompt
- How an **intent router** classifies user requests automatically
- How a **skill dispatcher** routes to the correct tool
- The foundation of the **ReAct pattern** (Reasoning + Acting)

### The Big Idea

```
Generic agent (bad):              Tool agent (good):
"Help me with this code"         "debug this code"
        ↓                               ↓
One prompt tries to do          Intent Router detects: DEBUG
everything → mediocre                   ↓
results                         Debug Skill runs with a
                                focused debugging prompt
                                → excellent results
```

**One agent, multiple specialised skills. The right tool for the right job.**

---

## 2. How It Works

### Architecture

```
User: "debug this code, it crashes"
           ↓
   ┌─────────────────┐
   │  Intent Router  │  ← reads keywords in the request
   │  detect_intent()│  ← returns: 'debug'
   └────────┬────────┘
            ↓
   ┌─────────────────┐
   │Skill Dispatcher │  ← picks the right prompt
   │  run_skill()    │  ← formats it with user's code
   └────────┬────────┘
            ↓
   ┌─────────────────┐
   │   Debug Skill   │  ← focused prompt: find bug, explain, fix
   │  DEBUG_PROMPT   │
   └────────┬────────┘
            ↓
          Mistral
            ↓
   "BUG FOUND: Division by zero at line 8..."
```

### Why Specialised Prompts Matter

Each skill prompt tells Mistral exactly:
- What **role** to play (expert debugger / tutor / senior dev)
- What **structure** to follow (numbered sections)
- What **output** to produce (bug + fix / explanation / review)

A focused prompt produces a structured, useful answer.  
A generic prompt produces a vague, unfocused answer.

---

## 3. Setup and Run Commands

On Mac:
```bash
cd stage3_tool_agent
source venv/bin/activate   # or reuse Stage 1/2 venv
pip install -r requirements.txt
python run.py
```

On Windows:
```bash
cd stage3_tool_agent
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

## 4. Expected Output

```
============================================================
CodePilot AI Studio — Stage 3: Tool Agent
============================================================

────────────────────────────────────────────────────────────
👤 User request: Can you debug this code? It crashes with empty list.
🧠 Detected intent: debug
🔧 Routing to: Debug Skill

🤖 CodePilot:
1. BUG FOUND: ZeroDivisionError when empty list passed to calculate_average()
2. WHY IT HAPPENS: len([]) returns 0, and dividing by 0 raises ZeroDivisionError
3. FIXED CODE:
   def calculate_average(numbers):
       if not numbers:           # check for empty list first
           return 0
       total = sum(numbers)
       return total / len(numbers)
4. EXPLANATION: Added a guard clause to handle the empty list edge case

────────────────────────────────────────────────────────────
👤 User request: Can you explain what this code does?
🧠 Detected intent: explain
📖 Routing to: Explain Skill
...
```

---

## 5. Code Walkthrough

### Intent Detection
```python
def detect_intent(user_request: str) -> str:
    request_lower = user_request.lower()     # case insensitive
    debug_keywords = ["debug", "fix", "error", "bug", ...]
    if any(keyword in request_lower for keyword in debug_keywords):
        return "debug"
    ...
```
`any()` + `in` is an elegant way to check if ANY keyword from a list appears in the request.  
`lower()` ensures "Debug", "DEBUG", "debug" all match.

### Skill Prompts
```python
DEBUG_PROMPT = PromptTemplate(
    input_variables=["code"],
    template="""You are an expert Python debugger...
1. BUG FOUND: ...
2. WHY IT HAPPENS: ...
3. FIXED CODE: ...
4. EXPLANATION: ..."""
)
```
The numbered structure in the prompt forces Mistral to give a structured answer.  
Without structure, the response is a wall of text that is hard to read.

### Dispatching to Skills
```python
def run_skill(intent: str, code: str) -> str:
    if intent == "debug":
        prompt = DEBUG_PROMPT.format(code=code)   # fill in {code}
    elif intent == "explain":
        prompt = EXPLAIN_PROMPT.format(code=code)
    ...
    return llm.invoke(prompt)   # send to Mistral
```
`.format(code=code)` replaces `{code}` in the template with the actual code string.

---

## 6. Common Errors and Fixes

### ❌ All requests route to "unknown"
**Cause:** Your request doesn't contain any keywords from the lists.  
**Fix:** Add more keywords to the relevant list, or change your test request to include a keyword like "debug" or "explain".

### ❌ `FileNotFoundError` for sample_code/buggy_sample.py
**Cause:** The sample code file doesn't exist yet.  
**Fix:** The script has a fallback — it uses inline code instead. Or run `python run.py` from the repo root.

### ❌ Response has no structure (just a paragraph)
**Cause:** The prompt template is not strict enough.  
**Fix:** Add "You MUST follow this exact structure" to the prompt and number the sections clearly.

---

## 7. Try It Yourself

**Experiment 1 — Add an "optimize" skill**  
Add a new `OPTIMIZE_PROMPT` that asks Mistral to improve code performance.  
Add "optimize", "slow", "performance", "speed" to a new keyword list.  
Wire it into `detect_intent()` and `run_skill()`.

**Experiment 2 — Test edge cases**  
What happens with these requests?
```
"debug and explain this code"   # mixed intent
"help me"                       # no clear intent  
"this is great code"            # positive but no intent
```

**Experiment 3 — Improve the router**  
Replace keyword matching with an LLM-based router:
```python
def detect_intent_with_llm(request: str) -> str:
    router_prompt = f"""Classify this request into ONE word: debug, explain, review, or unknown.
Request: {request}
Answer with ONE word only:"""
    return llm.invoke(router_prompt).strip().lower()
```
Is it more accurate? When does it fail?

---

## Key Concepts Summary

| Concept | What it means |
|---------|--------------|
| Tool orchestration | Routing tasks to specialised skills |
| Intent detection | Classifying what the user wants to do |
| PromptTemplate | Reusable prompt with fill-in variables |
| Skill dispatcher | The function that picks the right tool |
| ReAct pattern | Reasoning (intent) + Acting (skill call) |

---

## What's Next?

In **Stage 4** we add **RAG (Retrieval Augmented Generation)** — long-term memory using ChromaDB.  
The agent will store past bug fixes and retrieve relevant ones to help with new bugs.

➡️ Move to [`../stage4_rag_explain/`](../stage4_rag_explain/README.md)
