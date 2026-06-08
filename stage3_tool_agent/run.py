# ============================================================
# CodePilot AI Studio — Stage 3: Tool Agent
# ============================================================
# Concept  : Tool Orchestration — Intent routing to agent skills
# Framework: LangChain + Ollama
# Model    : Mistral (local)
#
# What you will learn:
#   - What "tool orchestration" means in agentic AI
#   - How to detect user intent (debug vs explain vs review)
#   - How to route different intents to different agent skills
#   - How each "skill" is a focused prompt with one job
#   - The ReAct pattern: Reasoning + Acting
#
# The problem we are solving:
#   A single generic prompt tries to do everything and does
#   nothing well. Tool orchestration lets us build SPECIALISED
#   skills — one for debugging, one for explaining, one for review.
#   The intent router picks the right skill automatically.
#
# Run this file:
#   python run.py
#
# Architecture:
#   User input
#       ↓
#   Intent Router  ← detects: debug / explain / review / unknown
#       ↓
#   ┌───────────┬──────────────┬──────────────┐
#   debug()   explain()    review()       unknown()
#   skill      skill        skill          fallback
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
from langchain_ollama import OllamaLLM      # local LLM
from langchain.prompts import PromptTemplate # structured prompts
import pathlib                               # cross-platform file paths (Mac + Windows)

# ── STEP 1: Connect to local LLM ─────────────────────────────
llm = OllamaLLM(model="mistral", temperature=0.3)
# temperature=0.3 → more deterministic for code tasks
# lower temperature = more precise, less creative

# ── STEP 2: Define skill prompts ─────────────────────────────
# Each skill is a FOCUSED prompt with ONE specific job.
# Specialised prompts produce much better results than generic ones.
# This is the "separation of concerns" principle applied to AI.

# --- Skill 1: Debug ---
# Job: Find the bug, explain why it happens, provide the fix
DEBUG_PROMPT = PromptTemplate(
    input_variables=["code"],   # only needs the buggy code
    template="""You are an expert Python debugger.
Analyse the following Python code carefully.

Your response MUST follow this exact structure:
1. BUG FOUND: [one line describing the bug]
2. WHY IT HAPPENS: [explain the root cause clearly]
3. FIXED CODE: [show the corrected code in a code block]
4. EXPLANATION: [explain what you changed and why]

Code to debug:
```python
{code}
```

Be specific. Point to the exact line number where the bug is."""
)

# --- Skill 2: Explain ---
# Job: Explain what the code does in plain English
EXPLAIN_PROMPT = PromptTemplate(
    input_variables=["code"],   # only needs the code to explain
    template="""You are a patient Python tutor explaining code to a beginner.
Explain the following Python code in simple, clear language.

Your response MUST follow this exact structure:
1. WHAT IT DOES: [one sentence summary]
2. HOW IT WORKS: [step by step walkthrough, plain English]
3. KEY CONCEPTS: [list any important Python concepts used]
4. BEGINNER TIP: [one practical tip for understanding this better]

Code to explain:
```python
{code}
```

Use simple language. Avoid jargon. Imagine explaining to a first-year student."""
)

# --- Skill 3: Review ---
# Job: Code review — quality, style, best practices
REVIEW_PROMPT = PromptTemplate(
    input_variables=["code"],   # only needs the code to review
    template="""You are a senior Python developer doing a code review.
Review the following Python code for quality, style, and best practices.

Your response MUST follow this exact structure:
1. OVERALL QUALITY: [score out of 10 with one sentence reason]
2. ISSUES FOUND: [list each issue with line number if possible]
3. BEST PRACTICE VIOLATIONS: [PEP8, naming, structure issues]
4. SUGGESTED IMPROVEMENTS: [specific code suggestions]
5. POSITIVE ASPECTS: [what is done well]

Code to review:
```python
{code}
```

Be constructive. The goal is to help the developer improve."""
)

# ── STEP 3: Define the Intent Router ─────────────────────────
# The intent router reads the user's request and decides
# which skill to use. It uses keywords and context clues.
# In production systems this could be another LLM call,
# but keyword matching is simpler and faster for teaching.

def detect_intent(user_request: str) -> str:
    """
    Detect what the user wants to do with their code.
    Returns one of: 'debug', 'explain', 'review', 'unknown'

    How it works:
    - Convert request to lowercase for case-insensitive matching
    - Check for keywords associated with each skill
    - Return the matching intent, or 'unknown' if no match
    """
    # normalise to lowercase so "Debug" and "debug" both match
    request_lower = user_request.lower()

    # --- Debug intent keywords ---
    # User wants to find and fix a bug
    debug_keywords = ["debug", "fix", "error", "bug", "broken",
                      "not working", "fails", "crash", "wrong output",
                      "exception", "traceback"]

    # --- Explain intent keywords ---
    # User wants to understand what code does
    explain_keywords = ["explain", "what does", "understand", "how does",
                        "what is", "describe", "tell me about", "walk me through"]

    # --- Review intent keywords ---
    # User wants code quality feedback
    review_keywords = ["review", "improve", "better", "quality", "best practice",
                       "refactor", "clean", "feedback", "suggestions"]

    # Check each keyword list — return first match found
    if any(keyword in request_lower for keyword in debug_keywords):
        return "debug"
    elif any(keyword in request_lower for keyword in explain_keywords):
        return "explain"
    elif any(keyword in request_lower for keyword in review_keywords):
        return "review"
    else:
        return "unknown"   # no clear intent detected


# ── STEP 4: Define the skill dispatcher ──────────────────────
# The dispatcher receives the detected intent and routes
# the code to the correct skill prompt + LLM call.
# Each skill gets its own focused prompt for best results.

def run_skill(intent: str, code: str) -> str:
    """
    Run the appropriate skill based on detected intent.

    Args:
        intent: 'debug', 'explain', 'review', or 'unknown'
        code:   the Python code to process

    Returns:
        The LLM's response as a string
    """
    if intent == "debug":
        # format the debug prompt with the user's code
        prompt = DEBUG_PROMPT.format(code=code)
        print("🔧 Routing to: Debug Skill")

    elif intent == "explain":
        # format the explain prompt with the user's code
        prompt = EXPLAIN_PROMPT.format(code=code)
        print("📖 Routing to: Explain Skill")

    elif intent == "review":
        # format the review prompt with the user's code
        prompt = REVIEW_PROMPT.format(code=code)
        print("🔍 Routing to: Review Skill")

    else:
        # fallback for unrecognised intent
        print("❓ Unknown intent — using generic skill")
        prompt = f"Please help with the following Python code:\n```python\n{code}\n```"

    # send the formatted prompt to Mistral and return the response
    return llm.invoke(prompt)


# ── STEP 5: Main agent loop ───────────────────────────────────
# This is the entry point — we test all three skills with
# different requests to demonstrate intent routing in action.

def main():
    print("=" * 60)
    print("CodePilot AI Studio — Stage 3: Tool Agent")
    print("=" * 60)
    print("Demonstrating intent routing to specialised skills...")
    print()

    # --- Load sample buggy code from file ---
    # pathlib.Path works on BOTH Mac (/) and Windows (\)
    sample_file = pathlib.Path(__file__).parent.parent / "sample_code" / "buggy_sample.py"

    if sample_file.exists():
        code = sample_file.read_text()   # read the buggy code
    else:
        # fallback inline code if sample file not found
        code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    average = total / len(numbers)
    return average

scores = [85, 92, 78, 90, 88]
print(calculate_average(scores))
print(calculate_average([]))    # this will crash!
"""

    # --- Test 1: Debug request ---
    print("─" * 60)
    request1 = "Can you debug this code? It crashes when I pass an empty list."
    print(f"👤 User request: {request1}")
    print()

    intent1 = detect_intent(request1)       # detect intent first
    print(f"🧠 Detected intent: {intent1}")

    response1 = run_skill(intent1, code)    # route to correct skill
    print(f"\n🤖 CodePilot:\n{response1}")
    print()

    # --- Test 2: Explain request ---
    print("─" * 60)
    request2 = "Can you explain what this code does?"
    print(f"👤 User request: {request2}")
    print()

    intent2 = detect_intent(request2)
    print(f"🧠 Detected intent: {intent2}")

    response2 = run_skill(intent2, code)
    print(f"\n🤖 CodePilot:\n{response2}")
    print()

    # --- Test 3: Review request ---
    print("─" * 60)
    request3 = "Please review this code and suggest improvements."
    print(f"👤 User request: {request3}")
    print()

    intent3 = detect_intent(request3)
    print(f"🧠 Detected intent: {intent3}")

    response3 = run_skill(intent3, code)
    print(f"\n🤖 CodePilot:\n{response3}")

    print()
    print("=" * 60)
    print("✅ Stage 3 complete! Tool orchestration is working.")
    print()
    print("KEY INSIGHT: Same code, 3 different requests → 3 different skills.")
    print("The intent router picks the right tool automatically.")


# ── ENTRY POINT ───────────────────────────────────────────────
# This ensures main() only runs when we execute this file directly,
# not when it is imported by another module (like app_final)
if __name__ == "__main__":
    main()

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Add a new intent: "optimize" — write a prompt that focuses on performance
# 2. Change a debug keyword to something unexpected — does routing break?
# 3. Try a request with mixed intent: "debug and explain this code"
#    What does detect_intent() return? Is that correct?
# 4. Change temperature from 0.3 to 0.9 — how do responses change?
