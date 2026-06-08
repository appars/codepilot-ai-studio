# Stage 6 — LangGraph Workflow 🕸️

> **Concept:** Stateful graph execution with conditional branching + simulated multi-agent system (AutoGen concept).

---

## 1. What You Will Learn

- Why **linear chains are not enough** for real agent workflows
- What a **StateGraph** is — nodes, edges, conditional routing
- How **state flows** between nodes like a shared whiteboard
- How **conditional edges** create dynamic branching and loops
- How to simulate **multi-agent conversation** (the AutoGen concept)

### LangChain vs LangGraph

```
LangChain (linear):          LangGraph (dynamic):

A → B → C → END             A → B → C
                                     ↓
Always the same path.        Good enough? YES → END
Cannot loop back.                         NO  → back to A
Cannot branch.
                             Path decided at runtime by the agent!
```

---

## 2. How It Works

### The State Object

```python
class AgentState(TypedDict):
    code: str          # original buggy code — never changes
    analysis: str      # written by analyze_node
    fix: str           # written by fix_node
    critique: str      # written by reflect_node
    iteration: int     # incremented by fix_node
    approved: bool     # set by reflect_node
    final_output: str  # the answer returned to the user
```

Think of `AgentState` as a **shared whiteboard** in a team meeting room.  
Every node reads from it and writes to it.  
No node needs to pass data directly to another — they all use state.

### Graph Structure

```
         START
           ↓
    ┌─────────────┐
    │ analyze_node│  ← reads: code
    │             │  ← writes: analysis
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │  fix_node   │  ← reads: code, analysis
    │             │  ← writes: fix, iteration
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │reflect_node │  ← reads: code, fix, iteration
    │             │  ← writes: critique, approved, final_output
    └──────┬──────┘
           ↓
    should_continue()
     ├── "end"     → END ✅
     └── "analyze" → back to analyze_node 🔄
```

---

## 3. Setup and Run Commands

On Mac:
```bash
cd stage6_langgraph_workflow
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

On Windows:
```bash
cd stage6_langgraph_workflow
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

⚠️ This stage makes the most LLM calls — allow 5–10 minutes on student laptops.

---

## 4. Expected Output

```
PART 1: LangGraph Stateful Workflow
Building graph...
✅ Graph compiled. Starting execution...

  [Node: ANALYZE] Iteration 1
  Analysis complete (523 chars)
  → Completed node: analyze

  [Node: FIX] Creating fix based on analysis...
  Fix generated (687 chars)
  → Completed node: fix

  [Node: REFLECT] Critiquing fix (iteration 1)...
  Critique complete (412 chars)
  ⚠️  Needs more work. Looping back...
  → Completed node: reflect

  [Node: ANALYZE] Iteration 2
  ...
  ✅ Fix APPROVED!

LANGGRAPH FINAL RESULT:
✅ CodePilot Fix (approved after 2 iteration(s))
def divide_all(numbers, divisor):
    if divisor == 0:
        raise ValueError("divisor cannot be zero")
    ...

PART 2: Multi-Agent Review (AutoGen Concept)
  [Debugger Agent] Generating fix...
  [Reviewer Agent] Reviewing DebuggerBot's fix...
```

---

## 5. Code Walkthrough

### Building the Graph
```python
graph = StateGraph(AgentState)   # create graph with our state schema
graph.add_node("analyze", analyze_node)
graph.add_node("fix", fix_node)
graph.add_node("reflect", reflect_node)
graph.add_edge("analyze", "fix")    # unconditional: always goes here
graph.add_edge("fix", "reflect")    # unconditional: always goes here
graph.add_conditional_edges(
    "reflect",          # from this node
    should_continue,    # call this function
    {"analyze": "analyze", "end": END}
)
graph.set_entry_point("analyze")
app = graph.compile()   # validate and prepare
```

### The Conditional Routing Function
```python
def should_continue(state: AgentState) -> str:
    if state["approved"]:
        return "end"             # go to END
    elif state["iteration"] >= MAX_ITERATIONS:
        return "end"             # safety limit
    else:
        return "analyze"         # loop back
```
This function returns a **string key** that maps to a node name.  
The graph uses this to pick the next destination dynamically.

### Running the Graph
```python
for step in app.stream(initial_state):
    node_name = list(step.keys())[0]
    print(f"Completed node: {node_name}")
    final_state = step[node_name]
```
`app.stream()` executes the graph and **yields state after each node**.  
This lets you watch the graph execute in real time — great for teaching!

---

## 6. Common Errors and Fixes

### ❌ `ModuleNotFoundError: No module named 'langgraph'`
**Fix:** `pip install -r requirements.txt` (with venv active)

### ❌ `ValueError: Node X not found`
**Cause:** Node name in `add_edge()` doesn't match node name in `add_node()`.  
**Fix:** Check all node names are spelled identically.

### ❌ Graph runs forever (never reaches END)
**Cause:** `should_continue()` never returns "end" / `approved` never becomes True.  
**Fix:** Lower `MAX_ITERATIONS` to 1 to force termination. Then debug the approval check.

### ❌ `KeyError` in node function
**Cause:** Trying to read a state key that doesn't exist yet.  
**Fix:** Make sure all state fields are set in `initial_state` before running the graph.

---

## 7. Try It Yourself

**Experiment 1 — Add a new node**
Add a `document_node` after `reflect_node` that writes a docstring for the fixed code:
```python
def document_node(state: AgentState) -> dict:
    prompt = f"Write a docstring for this fixed code:\n{state['fix']}"
    docstring = llm.invoke(prompt)
    return {"final_output": docstring + "\n\n" + state["fix"]}

graph.add_node("document", document_node)
# Update edges: reflect → document → END
```

**Experiment 2 — Watch the state evolve**
After each node, print the full state:
```python
for step in app.stream(initial_state):
    node_name = list(step.keys())[0]
    state = step[node_name]
    print(f"\n=== After {node_name} ===")
    print(f"iteration: {state.get('iteration', 0)}")
    print(f"approved: {state.get('approved', False)}")
    print(f"analysis length: {len(state.get('analysis', ''))}")
```

**Experiment 3 — Extend the multi-agent system**
Add a third agent — DocumenterBot:
```python
documenter_prompt = f"""You are DocumenterBot.
Write a complete docstring for this fixed function:
{reviewer_response}
Include: what it does, parameters, return value, raises."""
documenter_response = llm.invoke(documenter_prompt)
```

---

## Key Concepts Summary

| Concept | What it means |
|---------|--------------|
| StateGraph | A graph where nodes share a typed state object |
| Node | A Python function that reads/writes state |
| Edge | A connection between two nodes |
| Conditional edge | An edge that routes dynamically based on state |
| `should_continue()` | A function that returns the next node name |
| `compile()` | Validates and prepares the graph for execution |
| `stream()` | Runs the graph and yields state after each node |
| Multi-agent | Multiple specialised agents collaborating via message passing |

---

## Congratulations! 🎉

You have now built a complete CodePilot AI Studio with:

- ✅ Stage 1: Local LLM with Ollama
- ✅ Stage 2: Short-term memory
- ✅ Stage 3: Tool orchestration
- ✅ Stage 4: RAG long-term memory
- ✅ Stage 5: Reflection and self-improvement
- ✅ Stage 6: LangGraph stateful workflow + multi-agent

➡️ Now build the complete app: [`../app_final/`](../app_final/README.md)
