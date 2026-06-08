# Stage 5 — Reflection & Self-Improvement 🔄

> **Concept:** The agent generates a fix, critiques its own output, and improves it — automatically, without human intervention.

---

## 1. What You Will Learn

- What a **reflection loop** is in agentic AI
- How **Generate → Critique → Improve** works in practice
- Why self-critique produces dramatically better output
- How to **stop early** when the fix is good enough
- Why this pattern separates basic agents from production-grade ones

### The Human Analogy

```
Student WITHOUT reflection:        Student WITH reflection:
Write exam answer → submit         Write answer → re-read →
                                   "Wait, I missed the edge case"
Result: mediocre                   → fix it → re-read again
                                   → "Now it's complete" → submit

                                   Result: much better
```

**The reflection loop gives the agent this same self-awareness.**

---

## 2. How It Works

```
         ┌─────────────────────────────────────────┐
         │                                         │ (loop if NEEDS_IMPROVEMENT)
         ▼                                         │
   Generate Fix                              Improve Fix
   (GENERATE_PROMPT)                        (IMPROVE_PROMPT)
         │                                         ▲
         ▼                                         │
   Critique Fix ──── NEEDS_IMPROVEMENT ────────────┘
   (CRITIQUE_PROMPT)
         │
    APPROVED
         │
         ▼
   Return Final Fix ✅
```

### The Three Prompts

| Prompt | Role | Asks the model to... |
|--------|------|---------------------|
| `GENERATE_PROMPT` | Junior developer | Write a first fix |
| `CRITIQUE_PROMPT` | Senior engineer | Review the fix harshly |
| `IMPROVE_PROMPT` | Expert developer | Fix based on the feedback |

Three different "personas" — same model, different instructions.

---

## 3. Setup and Run Commands

On Mac:
```bash
cd stage5_reflection_review
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

On Windows:
```bash
cd stage5_reflection_review
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

⚠️ **This stage takes longer** — it makes 3–5 LLM calls instead of 1. Expected time: 2–5 minutes on a student laptop.

---

## 4. Expected Output

```
============================================================
CodePilot AI Studio — Stage 5: Reflection & Review
============================================================

  🔨 Step 1: Generating initial fix...
  Initial fix generated (412 chars)

  🔍 Step 2 (iteration 1): Critiquing the fix...
  Critique generated (387 chars)
  ⚠️  Critique says NEEDS_IMPROVEMENT. Improving...
  Improved fix generated (634 chars)

  🔍 Step 2 (iteration 2): Critiquing the fix...
  Critique generated (298 chars)
  ✅ Critique APPROVED the fix after 2 iteration(s)!

============================================================
REFLECTION LOOP RESULTS
============================================================

📝 INITIAL FIX (before reflection):
1. Bug found: ZeroDivisionError when empty list passed
2. Fixed code: added if len(numbers) == 0: return 0
...

🔍 CRITIQUE #1:
IS THE FIX CORRECT? Partially — handles empty list but not wrong types.
EDGE CASES MISSED: String input like "hello" would still crash.
VERDICT: NEEDS_IMPROVEMENT — add type checking.

✨ FINAL FIX (after reflection):
def calculate_average(numbers):
    if not isinstance(numbers, list):
        raise TypeError(f"Expected list, got {type(numbers).__name__}")
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
...

============================================================
REFLECTION SUMMARY
============================================================
  Improvement iterations : 2
  Critique approved      : True
  Initial fix length     : 412 characters
  Final fix length       : 634 characters
  Improvement            : +222 characters of detail
```

---

## 5. Code Walkthrough

### The Reflection Loop Logic
```python
for iteration in range(max_iterations):
    critique = llm.invoke(critique_prompt)    # critique current fix

    if "APPROVED" in critique.upper():
        results["approved"] = True
        break                                  # stop early — good enough!

    current_fix = llm.invoke(improve_prompt)  # improve based on critique
```

The `break` on approval is crucial — we don't keep iterating unnecessarily.  
This is how production systems work: stop when good enough, not after N fixed steps.

### Why Three Separate Prompts?

```python
# Junior developer mindset → generates first attempt
GENERATE_PROMPT = "You are a debugging assistant. Fix this code..."

# Senior engineer mindset → harsh critic
CRITIQUE_PROMPT = "You are a strict senior engineer reviewing a junior's fix..."

# Expert mindset → incorporates feedback
IMPROVE_PROMPT = "You are an expert improving based on code review..."
```

The same Mistral model behaves very differently based on the role given in the prompt.  
This is **prompt engineering** — one of the most powerful tools in agentic AI.

### The `max_iterations` Safety Guard
```python
def reflection_review(code: str, max_iterations: int = 2) -> dict:
```
Always have a maximum iteration limit.  
Without it, a stubborn critique could loop forever.  
In production, 2–3 iterations is usually sufficient and cost-effective.

---

## 6. Common Errors and Fixes

### ❌ Takes too long (more than 10 minutes)
**Cause:** Each reflection iteration is a separate LLM call. With `max_iterations=2` that is up to 5 calls total.  
**Fix:** Reduce to `max_iterations=1` for a quicker demo. Quality is still improved.

### ❌ Critique always says APPROVED (no improvement happens)
**Cause:** The critique prompt is not strict enough, or the initial fix is actually good.  
**Fix:** Make `CRITIQUE_PROMPT` stricter: add "Always find at least one thing to improve."

### ❌ Critique always says NEEDS_IMPROVEMENT (loops max times)
**Cause:** The initial code has many issues, or the critique is too harsh.  
**Fix:** This is actually fine — the max_iterations guard catches it. The final fix will still be improved.

### ❌ `"APPROVED" in critique.upper()` check misses approvals
**Cause:** Model writes "I approve this" instead of "APPROVED".  
**Fix:** Add more approval phrases to the check:
```python
approved_phrases = ["APPROVED", "I APPROVE", "FIX IS CORRECT", "LOOKS GOOD"]
if any(phrase in critique.upper() for phrase in approved_phrases):
```

---

## 7. Try It Yourself

**Experiment 1 — Compare initial vs final**
```python
print("INITIAL:")
print(results["initial_fix"])
print("\nFINAL:")
print(results["final_fix"])
```
List every specific improvement the reflection loop made. Can you see them clearly?

**Experiment 2 — Make critique stricter**
Add to `CRITIQUE_PROMPT`:
```
"You MUST find at least 2 issues. If the code looks correct, look harder.
Check: docstrings, type hints, error messages, PEP 8 compliance."
```
Does the final fix improve more?

**Experiment 3 — Try with good code**
Pass this code (which has no bugs) to `reflection_review()`:
```python
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b
```
Does the critique recognise it is correct and APPROVE immediately?

**Experiment 4 — Count the LLM calls**
Add a counter to track how many times `llm.invoke()` is called.  
With `max_iterations=2`: minimum 2 calls (generate + critique), maximum 5 calls.

---

## Key Concepts Summary

| Concept | What it means |
|---------|--------------|
| Reflection loop | Agent evaluates and improves its own output |
| Generate → Critique → Improve | The three phases of self-improvement |
| Early stopping | Exit the loop when quality is good enough |
| `max_iterations` | Safety limit to prevent infinite improvement loops |
| Prompt personas | Using different role descriptions for different tasks |
| Self-improvement | Agent gets better without human feedback |

---

## What's Next?

In **Stage 6** we add **LangGraph** — a stateful workflow graph that wires all these concepts together into a proper agentic pipeline, plus a simulated multi-agent system (AutoGen concept).

➡️ Move to [`../stage6_langgraph_workflow/`](../stage6_langgraph_workflow/README.md)
