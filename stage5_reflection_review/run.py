# ============================================================
# CodePilot AI Studio — Stage 5: Reflection & Self-Improvement
# ============================================================
# Concept  : Reflection loops — the agent critiques and improves
#            its own output before returning it to the user
# Framework: LangChain + Ollama
# Model    : Mistral (local)
#
# What you will learn:
#   - What a reflection loop is and why it improves output quality
#   - How to make an agent critique its own response
#   - How the Generate → Critique → Improve cycle works
#   - Why self-improvement separates basic agents from great ones
#   - How to control the number of reflection iterations
#
# The problem we are solving:
#   A single LLM call often produces a "good enough" answer.
#   But with reflection, the agent asks itself:
#     "Is this the BEST answer I can give?"
#   If not, it improves — just like a student reviewing their
#   own exam paper before submitting it.
#
# The reflection loop:
#   ┌─────────────────────────────────────────────┐
#   │                                             │
#   ▼                                             │
# Generate fix → Critique fix → Good enough? → YES → Return
#                                    │
#                                   NO
#                                    │
#                               Improve fix
#                                    │
#                              (loop again)
#
# Run this file:
#   python run.py
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
from langchain_ollama import OllamaLLM       # local LLM
from langchain.prompts import PromptTemplate  # structured prompts

# ── STEP 1: Connect to local LLM ─────────────────────────────
llm = OllamaLLM(model="mistral", temperature=0.4)
# temperature=0.4 — slightly creative but still precise for code

# ── STEP 2: Define the generation prompt ─────────────────────
# This is the first pass — generate an initial fix for the bug.
# It does NOT need to be perfect — the reflection loop will improve it.
GENERATE_PROMPT = PromptTemplate(
    input_variables=["code"],
    template="""You are a Python debugging assistant.
Analyse this code and provide a fix.

Code:
```python
{code}
```

Provide:
1. The bug you found
2. The fixed code
3. A brief explanation

Be thorough but this is a first draft — it will be reviewed."""
)

# ── STEP 3: Define the critique prompt ───────────────────────
# This is the self-evaluation step — the agent reads its OWN fix
# and asks: "Is this actually correct and complete?"
# Critique is harsh and specific — that is what makes it useful.
CRITIQUE_PROMPT = PromptTemplate(
    input_variables=["original_code", "proposed_fix"],
    template="""You are a strict senior Python engineer reviewing a junior developer's fix.

Original buggy code:
```python
{original_code}
```

Proposed fix:
{proposed_fix}

Critically evaluate this fix:
1. IS THE FIX CORRECT? Does it actually solve the bug? (YES/NO + reason)
2. EDGE CASES MISSED: List any inputs that would still cause errors
3. CODE QUALITY: Any style, readability, or best practice issues?
4. MISSING ELEMENTS: What explanation or context is lacking?
5. VERDICT: APPROVED (fix is good) or NEEDS_IMPROVEMENT (explain what to fix)

Be strict. A good fix handles ALL edge cases, not just the obvious one."""
)

# ── STEP 4: Define the improvement prompt ────────────────────
# If the critique says NEEDS_IMPROVEMENT, this prompt takes
# the original fix + the critique feedback and produces a better fix.
# The agent learns from its own criticism.
IMPROVE_PROMPT = PromptTemplate(
    input_variables=["original_code", "previous_fix", "critique"],
    template="""You are a Python expert improving a fix based on code review feedback.

Original buggy code:
```python
{original_code}
```

Previous fix attempt:
{previous_fix}

Code review feedback:
{critique}

Now produce an IMPROVED fix that addresses ALL the feedback above:
1. IMPROVED FIX: [show the corrected code]
2. WHAT CHANGED: [list every improvement made based on the feedback]
3. EDGE CASES HANDLED: [show the fix handles all mentioned edge cases]
4. FINAL EXPLANATION: [clear explanation suitable for a student]

Make this the definitive, production-quality fix."""
)

# ── STEP 5: The reflection loop ───────────────────────────────
def reflection_review(code: str, max_iterations: int = 2) -> dict:
    """
    Run the full reflection loop:
    Generate → Critique → Improve (repeat if needed)

    Args:
        code:           the buggy Python code to fix
        max_iterations: maximum number of improve cycles (prevents infinite loops)

    Returns:
        dict with keys:
            'initial_fix'   : the first generated fix
            'critiques'     : list of critique responses
            'final_fix'     : the best fix after all iterations
            'iterations'    : how many improvement cycles ran
            'approved'      : whether critique approved the final fix
    """

    results = {
        "initial_fix": "",
        "critiques": [],
        "final_fix": "",
        "iterations": 0,
        "approved": False
    }

    # ── Iteration 0: Generate the first fix ──────────────────
    print("  🔨 Step 1: Generating initial fix...")
    initial_prompt = GENERATE_PROMPT.format(code=code)
    current_fix = llm.invoke(initial_prompt)   # first attempt
    results["initial_fix"] = current_fix
    print(f"  Initial fix generated ({len(current_fix)} chars)")

    # ── Reflection loop: Critique → Improve ──────────────────
    # We loop up to max_iterations times.
    # If critique APPROVES, we stop early — no need to keep improving.
    # This is the key insight: stop when good enough, not after fixed iterations.
    for iteration in range(max_iterations):

        print(f"\n  🔍 Step 2 (iteration {iteration + 1}): Critiquing the fix...")

        # Critique the current fix — is it actually good?
        critique_prompt = CRITIQUE_PROMPT.format(
            original_code=code,
            proposed_fix=current_fix
        )
        critique = llm.invoke(critique_prompt)
        results["critiques"].append(critique)
        results["iterations"] += 1

        print(f"  Critique generated ({len(critique)} chars)")

        # Check if critique approved the fix
        # We look for "APPROVED" in the critique response
        # (this is why we told the model to use that exact word)
        if "APPROVED" in critique.upper() and "NEEDS_IMPROVEMENT" not in critique.upper():
            print(f"  ✅ Critique APPROVED the fix after {iteration + 1} iteration(s)!")
            results["approved"] = True
            results["final_fix"] = current_fix   # use current fix as final
            break   # exit loop early — no more improvement needed

        # Critique said NEEDS_IMPROVEMENT — improve the fix
        print(f"  ⚠️  Critique says NEEDS_IMPROVEMENT. Improving...")

        improve_prompt = IMPROVE_PROMPT.format(
            original_code=code,
            previous_fix=current_fix,
            critique=critique
        )
        # The improved fix becomes the current fix for next iteration
        current_fix = llm.invoke(improve_prompt)
        print(f"  Improved fix generated ({len(current_fix)} chars)")

    # If loop completed without approval, use the last improved fix
    if not results["approved"]:
        print(f"\n  ℹ️  Max iterations ({max_iterations}) reached. Using best fix so far.")
        results["final_fix"] = current_fix

    return results


# ── STEP 6: Demo the reflection loop ─────────────────────────
def main():
    print("=" * 60)
    print("CodePilot AI Studio — Stage 5: Reflection & Review")
    print("=" * 60)
    print()

    # A buggy function with multiple issues:
    # 1. Division by zero when empty list passed
    # 2. No type checking
    # 3. No docstring
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

# Test calls
print(calculate_average([10, 20, 30]))
print(calculate_average([]))      # BUG: ZeroDivisionError!
print(calculate_average("hello")) # BUG: wrong type!
"""

    print("Buggy code to fix:")
    print(buggy_code)
    print("-" * 60)
    print("Starting reflection loop (Generate → Critique → Improve)...")
    print()

    # Run the reflection loop
    results = reflection_review(buggy_code, max_iterations=2)

    # ── Display results ───────────────────────────────────────
    print()
    print("=" * 60)
    print("REFLECTION LOOP RESULTS")
    print("=" * 60)

    # Show the initial fix
    print("\n📝 INITIAL FIX (before reflection):")
    print("-" * 40)
    print(results["initial_fix"])

    # Show each critique
    for i, critique in enumerate(results["critiques"]):
        print(f"\n🔍 CRITIQUE #{i+1}:")
        print("-" * 40)
        print(critique)

    # Show the final improved fix
    print("\n✨ FINAL FIX (after reflection):")
    print("-" * 40)
    print(results["final_fix"])

    # Summary stats
    print()
    print("=" * 60)
    print("REFLECTION SUMMARY")
    print("=" * 60)
    print(f"  Improvement iterations : {results['iterations']}")
    print(f"  Critique approved      : {results['approved']}")
    initial_len = len(results["initial_fix"])
    final_len   = len(results["final_fix"])
    print(f"  Initial fix length     : {initial_len} characters")
    print(f"  Final fix length       : {final_len} characters")
    print(f"  Improvement            : +{final_len - initial_len} characters of detail")
    print()
    print("✅ Stage 5 complete! Reflection loop is working.")
    print()
    print("KEY INSIGHT: The agent improved its own answer without")
    print("any human intervention. This is self-improvement.")


if __name__ == "__main__":
    main()

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Change max_iterations=2 to max_iterations=1 — how does quality change?
# 2. Make the CRITIQUE_PROMPT stricter — does the agent improve more?
# 3. Print results["initial_fix"] vs results["final_fix"] side by side
#    Can you clearly see what improved?
# 4. What happens if the initial fix is already correct?
#    Does the critique recognise that and approve immediately?
