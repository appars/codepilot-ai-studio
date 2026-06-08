# ============================================================
# CodePilot AI Studio — Stage 6: LangGraph Workflow
# ============================================================
# Concept  : Stateful graph-based agent workflow + simulated
#            multi-agent system (AutoGen concept)
# Framework: LangGraph + LangChain + Ollama
# Model    : Mistral (local)
#
# What you will learn:
#   - Why linear chains are not enough for complex agents
#   - What a StateGraph is — nodes, edges, and state
#   - How conditional edges create dynamic branching
#   - How state flows between nodes automatically
#   - How to simulate multi-agent conversation (AutoGen concept)
#
# Why LangGraph?
#   LangChain chains go A → B → C. Always linear. Always forward.
#   LangGraph goes A → B → C → back to A if needed.
#   It supports loops, conditions, and branching — essential for
#   any agent that needs to retry, reflect, or make decisions.
#
# Our graph:
#   START
#     ↓
#   analyze_node      ← understand the bug
#     ↓
#   fix_node          ← generate a fix
#     ↓
#   reflect_node      ← critique the fix
#     ↓
#   needs_more_work?
#     ├── YES → back to analyze_node (loop!)
#     └── NO  → END
#
# Run this file:
#   python run.py
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
from langchain_ollama import OllamaLLM           # local LLM
from langgraph.graph import StateGraph, END       # graph builder and END sentinel
from typing import TypedDict, Annotated           # type hints for state
import operator                                   # for Annotated list operations

# ── STEP 1: Define the Agent State ───────────────────────────
# State is the shared "memory" that flows between all nodes.
# Every node can READ from state and WRITE to state.
# TypedDict gives us type safety — we know exactly what's in state.
#
# Think of state like a shared whiteboard:
#   - analyze_node writes the analysis
#   - fix_node reads the analysis and writes the fix
#   - reflect_node reads the fix and writes the critique
#   - The graph decides what happens next based on state
class AgentState(TypedDict):
    code: str                    # the original buggy code (never changes)
    analysis: str                # output from analyze_node
    fix: str                     # output from fix_node
    critique: str                # output from reflect_node
    iteration: int               # how many fix attempts so far
    approved: bool               # did reflect_node approve the fix?
    final_output: str            # the final answer returned to user


# ── STEP 2: Connect to local LLM ─────────────────────────────
llm = OllamaLLM(model="mistral", temperature=0.3)


# ── STEP 3: Define each node ──────────────────────────────────
# Each node is a plain Python function that:
#   - Takes the current state as input
#   - Returns a DICTIONARY of state fields to UPDATE
#   - Does NOT need to return the full state — only changed fields
#
# LangGraph merges the returned dict into the existing state.

def analyze_node(state: AgentState) -> dict:
    """
    Node 1: Analyze the buggy code.
    Reads:  state["code"]
    Writes: state["analysis"]
    """
    print(f"\n  [Node: ANALYZE] Iteration {state['iteration'] + 1}")

    prompt = f"""You are a Python expert.
Analyse this buggy Python code and identify ALL issues.

Code:
```python
{state['code']}
```

Provide:
1. List every bug found (be specific about line numbers)
2. Root cause of each bug
3. What inputs would trigger each bug
Be thorough — missing a bug now means a broken fix later."""

    analysis = llm.invoke(prompt)
    print(f"  Analysis complete ({len(analysis)} chars)")

    # Return ONLY the fields this node changes
    return {"analysis": analysis}


def fix_node(state: AgentState) -> dict:
    """
    Node 2: Generate a fix based on the analysis.
    Reads:  state["code"], state["analysis"]
    Writes: state["fix"], state["iteration"]
    """
    print(f"\n  [Node: FIX] Creating fix based on analysis...")

    prompt = f"""You are a Python developer fixing bugs.

Original code:
```python
{state['code']}
```

Analysis of bugs:
{state['analysis']}

Provide the COMPLETE fixed code with:
1. All identified bugs fixed
2. Inline comments explaining each fix
3. Brief explanation of changes made

Show the FULL fixed function, not just the changed lines."""

    fix = llm.invoke(prompt)
    print(f"  Fix generated ({len(fix)} chars)")

    return {
        "fix": fix,
        "iteration": state["iteration"] + 1   # increment attempt counter
    }


def reflect_node(state: AgentState) -> dict:
    """
    Node 3: Critique the fix and decide if more work is needed.
    Reads:  state["code"], state["fix"], state["iteration"]
    Writes: state["critique"], state["approved"], state["final_output"]

    This node decides the FLOW of the graph:
    - Sets approved=True  → graph routes to END
    - Sets approved=False → graph routes back to analyze_node
    """
    print(f"\n  [Node: REFLECT] Critiquing fix (iteration {state['iteration']})...")

    prompt = f"""You are a strict senior Python developer doing code review.

Original buggy code:
```python
{state['code']}
```

Proposed fix:
{state['fix']}

Review the fix:
1. Does it fix ALL the bugs? List each bug and whether it is fixed.
2. Are there remaining issues or missed edge cases?
3. Is the code quality acceptable?

VERDICT (choose exactly one):
- Write APPROVED if all bugs are fixed and code quality is good
- Write NEEDS_IMPROVEMENT if any bugs remain or quality is poor
  (then explain specifically what still needs to be fixed)"""

    critique = llm.invoke(prompt)
    print(f"  Critique complete ({len(critique)} chars)")

    # Determine if fix is approved based on critique text
    # We check for "APPROVED" and ensure "NEEDS_IMPROVEMENT" is absent
    is_approved = (
        "APPROVED" in critique.upper() and
        "NEEDS_IMPROVEMENT" not in critique.upper()
    )

    # Build the final output message
    if is_approved:
        final_output = f"""✅ CodePilot Fix (approved after {state['iteration']} iteration(s))

{state['fix']}

Review: {critique[:200]}..."""
        print(f"  ✅ Fix APPROVED!")
    else:
        final_output = ""  # not done yet
        print(f"  ⚠️  Needs more work. Looping back to analyze...")

    return {
        "critique": critique,
        "approved": is_approved,
        "final_output": final_output
    }


# ── STEP 4: Define the conditional routing function ───────────
# This function reads state and returns the NAME of the next node.
# LangGraph uses this to decide where to go after reflect_node.
#
# This is the KEY difference from LangChain:
# LangChain: always A → B → C
# LangGraph: A → B → C → (back to A or END) — DYNAMIC!

def should_continue(state: AgentState) -> str:
    """
    Routing function: decides what happens after reflect_node.

    Returns:
        "analyze"  → if fix needs more work (loops back)
        "end"      → if fix is approved (graph terminates)

    Also enforces a maximum iteration limit to prevent infinite loops.
    """
    MAX_ITERATIONS = 2  # safety limit — never loop more than this

    if state["approved"]:
        # Critique approved — we're done!
        return "end"
    elif state["iteration"] >= MAX_ITERATIONS:
        # Hit the limit — stop even if not perfect
        print(f"\n  ℹ️  Max iterations ({MAX_ITERATIONS}) reached. Stopping.")
        return "end"
    else:
        # Not approved and not at limit — try again
        return "analyze"


# ── STEP 5: Simulated Multi-Agent Review (AutoGen concept) ────
# AutoGen runs multiple agents that converse with each other.
# True AutoGen requires complex setup — here we simulate it:
# Agent 1 (Debugger) generates a fix
# Agent 2 (Reviewer) critiques it
# They "converse" via their outputs — same concept, simpler code.

def multi_agent_review(code: str) -> str:
    """
    Simulate a two-agent conversation:
    - Debugger Agent: fixes the code
    - Reviewer Agent: reviews the fix

    This demonstrates the AutoGen pattern without full AutoGen setup.
    In real AutoGen, these agents would be separate processes
    that send messages to each other autonomously.
    """
    print("\n" + "─" * 40)
    print("🤖 MULTI-AGENT REVIEW (AutoGen concept)")
    print("─" * 40)

    # --- Agent 1: Debugger Agent ---
    print("\n  [Debugger Agent] Generating fix...")
    debugger_prompt = f"""You are DebuggerBot, a specialised Python debugging agent.
Your ONLY job is to find and fix bugs in Python code.
Be precise. Output the fix and nothing else.

Code: ```python\n{code}\n```

Output: Fixed code with brief inline comments."""

    debugger_response = llm.invoke(debugger_prompt)
    print(f"  DebuggerBot response: {debugger_response[:100]}...")

    # --- Agent 2: Reviewer Agent ---
    # Reviewer receives the Debugger's output — this is the "conversation"
    print("\n  [Reviewer Agent] Reviewing DebuggerBot's fix...")
    reviewer_prompt = f"""You are ReviewerBot, a strict Python code review agent.
Your ONLY job is to review fixes and approve or reject them.

Original code: ```python\n{code}\n```

DebuggerBot's fix:
{debugger_response}

Review the fix and respond with:
- APPROVED: [reason]
- or REJECTED: [specific issues]
Then provide your own improved version if rejected."""

    reviewer_response = llm.invoke(reviewer_prompt)
    print(f"  ReviewerBot response: {reviewer_response[:100]}...")

    # Combine both agents' outputs
    combined = f"""
=== DEBUGGER AGENT OUTPUT ===
{debugger_response}

=== REVIEWER AGENT VERDICT ===
{reviewer_response}
"""
    return combined


# ── STEP 6: Build the LangGraph ──────────────────────────────
def build_graph():
    """
    Build and compile the LangGraph StateGraph.

    Graph structure:
      START → analyze → fix → reflect → (conditional) → END or analyze
    """
    # Create the graph — pass our state class so LangGraph knows the schema
    graph = StateGraph(AgentState)

    # Add nodes — each node is a function we defined above
    graph.add_node("analyze", analyze_node)   # Node 1
    graph.add_node("fix", fix_node)           # Node 2
    graph.add_node("reflect", reflect_node)   # Node 3

    # Add edges — define the flow between nodes
    graph.add_edge("analyze", "fix")          # analyze always goes to fix
    graph.add_edge("fix", "reflect")          # fix always goes to reflect

    # Add CONDITIONAL edge — reflect can go to END or back to analyze
    graph.add_conditional_edges(
        "reflect",              # from this node
        should_continue,        # call this function to decide
        {
            "analyze": "analyze",   # if returns "analyze" → go to analyze node
            "end": END              # if returns "end"    → terminate graph
        }
    )

    # Set the starting node
    graph.set_entry_point("analyze")

    # Compile — this validates the graph and prepares it for execution
    return graph.compile()


# ── STEP 7: Run the demo ──────────────────────────────────────
def main():
    print("=" * 60)
    print("CodePilot AI Studio — Stage 6: LangGraph Workflow")
    print("=" * 60)
    print()

    # Sample buggy code
    buggy_code = """
def divide_all(numbers, divisor):
    results = []
    for num in numbers:
        results.append(num / divisor)
    return results

print(divide_all([10, 20, 30], 2))
print(divide_all([10, 20, 30], 0))  # BUG: ZeroDivisionError
print(divide_all([], 5))            # returns empty — is that right?
"""

    print("─" * 60)
    print("PART 1: LangGraph Stateful Workflow")
    print("─" * 60)
    print("Building graph...")

    # Build and compile the graph
    app = build_graph()
    print("✅ Graph compiled. Starting execution...")
    print()

    # Define the initial state — only set values we know at the start
    initial_state = {
        "code": buggy_code,
        "analysis": "",
        "fix": "",
        "critique": "",
        "iteration": 0,
        "approved": False,
        "final_output": ""
    }

    # Run the graph — it handles all routing automatically
    # stream() yields state after each node so we can watch progress
    final_state = None
    for step in app.stream(initial_state):
        # step is a dict: {node_name: updated_state}
        node_name = list(step.keys())[0]
        print(f"  → Completed node: {node_name}")
        final_state = step[node_name]

    # Display final result
    print()
    print("─" * 60)
    print("LANGGRAPH FINAL RESULT:")
    print("─" * 60)
    if final_state and final_state.get("final_output"):
        print(final_state["final_output"])
    else:
        print(final_state.get("fix", "No output generated"))

    # ── Part 2: Multi-Agent demo ─────────────────────────────
    print()
    print("─" * 60)
    print("PART 2: Multi-Agent Review (AutoGen Concept)")
    print("─" * 60)

    multi_agent_result = multi_agent_review(buggy_code)
    print(multi_agent_result)

    print()
    print("=" * 60)
    print("✅ Stage 6 complete! LangGraph + Multi-Agent working.")
    print()
    print("KEY INSIGHT: LangGraph gave us CONDITIONAL CONTROL FLOW.")
    print("The graph decided its own path based on the critique result.")
    print("This is the foundation of truly autonomous AI agents.")


if __name__ == "__main__":
    main()

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Add a new node: "test_node" that checks if the fix passes tests
#    Insert it between fix_node and reflect_node
# 2. Change MAX_ITERATIONS to 1 — does quality drop noticeably?
# 3. Print the full state after each node to see how state evolves
# 4. Add a "documentation_agent" to the multi-agent section
#    that auto-generates docstrings for the fixed code
