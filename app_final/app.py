# ============================================================
# CodePilot AI Studio — Final App
# ============================================================
# This is the COMPLETE application that combines all 6 stages:
#   Stage 1 → Ollama local LLM connection
#   Stage 2 → Conversation memory
#   Stage 3 → Intent routing to 3 skills (debug/explain/review)
#   Stage 4 → RAG with ChromaDB for knowledge retrieval
#   Stage 5 → Reflection loop for self-improvement
#   Stage 6 → LangGraph stateful workflow
#
# UI: Streamlit (browser-based, no HTML/CSS needed)
#
# Run this app:
#   streamlit run app.py
#
# Then open your browser at: http://localhost:8501
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
import streamlit as st                                           # the UI framework
import pathlib                                                   # cross-platform paths
from langchain_ollama import OllamaLLM                          # local LLM
from langchain.memory import ConversationBufferMemory            # short-term memory
from langchain.chains import ConversationChain                  # memory + LLM chain
from langchain.prompts import PromptTemplate                     # structured prompts
from langchain_huggingface import HuggingFaceEmbeddings          # text embeddings
from langchain_chroma import Chroma                              # vector database
from langgraph.graph import StateGraph, END                      # graph workflow
from typing import TypedDict                                     # state type hints

# ── PAGE CONFIGURATION ────────────────────────────────────────
# Must be the FIRST Streamlit command — configures the browser tab
st.set_page_config(
    page_title="CodePilot AI Studio",
    page_icon="🤖",
    layout="wide",          # use full browser width
    initial_sidebar_state="expanded"
)

# ── MODEL CONFIGURATION ───────────────────────────────────────
# Change MODEL_NAME here if students have low-RAM laptops
MODEL_NAME = "mistral"      # or "phi3:mini" for 4GB RAM laptops

# ── KNOWLEDGE BASE SETUP ─────────────────────────────────────
# Path to ChromaDB storage — persists across app restarts
DB_PATH = pathlib.Path(__file__).parent / "knowledge_db"

# Python knowledge for RAG — same as Stage 4
PYTHON_KNOWLEDGE = [
    """IndexError: Raised when a sequence subscript is out of range.
Occurs when accessing list/tuple index that doesn't exist.
Fix: Check len() before indexing, or use try/except IndexError.""",

    """ZeroDivisionError: Raised when dividing by zero.
Fix: Always validate denominator is non-zero before division.
Pattern: if divisor != 0: result = numerator / divisor""",

    """TypeError: Operation applied to object of wrong type.
Common: mixing strings and numbers without conversion.
Fix: Use isinstance() to check types, or str()/int()/float() to convert.""",

    """Python Best Practices: Use meaningful variable names.
Add docstrings to all functions. Handle edge cases explicitly.
Follow PEP 8 style. Use type hints for clarity.""",

    """Exception Handling: Use specific except clauses, not bare except.
Use try/except/finally for resource cleanup.
Always log or report errors — don't silently pass exceptions.""",

    """List Safety: Always check if a list is empty before accessing elements.
Use: if my_list: instead of if len(my_list) > 0:
Prefer list comprehensions over manual loops for clarity.""",
]

# ── CACHED RESOURCE LOADERS ───────────────────────────────────
# @st.cache_resource loads these ONCE and reuses across all rerenders.
# Without caching, Streamlit would recreate LLM/DB on every interaction.

@st.cache_resource
def load_llm():
    """Load and cache the local LLM connection."""
    return OllamaLLM(model=MODEL_NAME, temperature=0.3)


@st.cache_resource
def load_embeddings():
    """Load and cache the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


@st.cache_resource
def load_vectorstore():
    """Load or build the ChromaDB knowledge base."""
    embeddings = load_embeddings()

    if DB_PATH.exists() and any(DB_PATH.iterdir()):
        # Load existing knowledge base from disk
        return Chroma(
            collection_name="codepilot_knowledge",
            embedding_function=embeddings,
            persist_directory=str(DB_PATH)
        )
    else:
        # Build knowledge base from scratch
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document

        # Convert raw text to Document objects
        docs = [Document(page_content=text) for text in PYTHON_KNOWLEDGE]

        # Split into chunks for better retrieval
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        chunks = splitter.split_documents(docs)

        # Store in ChromaDB
        return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="codepilot_knowledge",
            persist_directory=str(DB_PATH)
        )


# ── SESSION STATE INITIALISATION ─────────────────────────────
# st.session_state persists data across Streamlit interactions.
# Without this, all data would reset on every button click.

def init_session_state():
    """Initialise all session state variables if not already set."""

    # Chat history for the conversation tab
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Conversation memory for the memory agent
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    # Track which skill was last used
    if "last_skill" not in st.session_state:
        st.session_state.last_skill = None


# ── SKILL FUNCTIONS ───────────────────────────────────────────
# Each skill uses a focused prompt — same pattern as Stage 3.

def skill_debug(code: str, llm) -> str:
    """Debug skill: find bugs, explain, fix."""
    prompt = f"""You are an expert Python debugger.
Analyse this code and provide a complete fix.

Code:
```python
{code}
```

Respond with:
## 🐛 Bug Found
[describe the bug clearly]

## 🔍 Root Cause
[explain WHY this happens]

## ✅ Fixed Code
```python
[show the complete fixed code]
```

## 📝 Explanation
[explain what you changed and why, suitable for a student]"""

    return llm.invoke(prompt)


def skill_explain(code: str, llm, vectorstore) -> str:
    """Explain skill: RAG-enhanced code explanation."""
    # Retrieve relevant knowledge first (Stage 4 pattern)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    relevant_docs = retriever.invoke(f"Python concepts errors: {code[:200]}")
    context = "\n".join([doc.page_content for doc in relevant_docs])

    prompt = f"""You are a patient Python tutor.
Use the knowledge below to give a thorough explanation.

Knowledge Base Context:
{context}

Explain this Python code:
```python
{code}
```

Respond with:
## 📖 What It Does
[one sentence summary]

## 🔄 How It Works
[step by step walkthrough]

## ⚠️ Potential Issues
[any risks or edge cases, informed by the knowledge base]

## 💡 Beginner Tip
[one practical tip for a student]"""

    return llm.invoke(prompt)


def skill_review(code: str, llm) -> str:
    """Review skill: code quality with reflection loop."""
    # Step 1: Generate initial review
    initial_prompt = f"""You are a senior Python developer doing code review.

Code:
```python
{code}
```

Provide:
## 📊 Quality Score
[X/10 with brief reason]

## 🔴 Issues Found
[list each issue]

## ✅ Positive Aspects
[what is done well]

## 🛠️ Suggested Improvements
[specific code suggestions]"""

    initial_review = llm.invoke(initial_prompt)

    # Step 2: Reflect — critique the review itself (Stage 5 pattern)
    reflect_prompt = f"""Review this code review for completeness:

Code reviewed:
```python
{code}
```

Initial review:
{initial_review}

Is this review complete? Check:
- Did it find ALL issues?
- Did it suggest SPECIFIC improvements?
- Is it CONSTRUCTIVE for a student?

If APPROVED: return the review as-is with "✅ REVIEW APPROVED" at the top.
If needs work: return an improved version with "🔄 IMPROVED REVIEW" at the top."""

    final_review = llm.invoke(reflect_prompt)
    return final_review


def detect_intent(request: str) -> str:
    """Detect user intent from their request text."""
    request_lower = request.lower()

    debug_keywords   = ["debug", "fix", "error", "bug", "broken",
                        "crash", "not working", "exception", "wrong"]
    explain_keywords = ["explain", "what does", "understand", "how does",
                        "describe", "walk me through", "what is"]
    review_keywords  = ["review", "improve", "better", "quality",
                        "best practice", "refactor", "feedback", "clean"]

    if any(k in request_lower for k in debug_keywords):
        return "debug"
    elif any(k in request_lower for k in explain_keywords):
        return "explain"
    elif any(k in request_lower for k in review_keywords):
        return "review"
    else:
        return "debug"   # default to debug for code submissions


# ── LANGGRAPH STATE AND GRAPH ─────────────────────────────────
class AgentState(TypedDict):
    code: str
    analysis: str
    fix: str
    critique: str
    iteration: int
    approved: bool
    final_output: str


def build_debug_graph(llm):
    """Build the LangGraph debug workflow (Stage 6 pattern)."""

    def analyze(state):
        result = llm.invoke(
            f"Analyse ALL bugs in this Python code:\n```python\n{state['code']}\n```\n"
            f"List each bug, its cause, and what input triggers it."
        )
        return {"analysis": result}

    def fix(state):
        result = llm.invoke(
            f"Fix ALL bugs found:\n\nCode:\n```python\n{state['code']}\n```\n\n"
            f"Analysis:\n{state['analysis']}\n\n"
            f"Provide the complete fixed code with inline comments."
        )
        return {"fix": result, "iteration": state["iteration"] + 1}

    def reflect(state):
        result = llm.invoke(
            f"Review this fix:\n\nOriginal:\n```python\n{state['code']}\n```\n\n"
            f"Fix:\n{state['fix']}\n\n"
            f"Is it complete? Write APPROVED or NEEDS_IMPROVEMENT + reason."
        )
        approved = "APPROVED" in result.upper() and "NEEDS_IMPROVEMENT" not in result.upper()
        final = f"**Fix (iteration {state['iteration']}):**\n{state['fix']}\n\n**Review:**\n{result}" if approved else ""
        return {"critique": result, "approved": approved, "final_output": final}

    def route(state):
        if state["approved"] or state["iteration"] >= 2:
            return "end"
        return "analyze"

    g = StateGraph(AgentState)
    g.add_node("analyze", analyze)
    g.add_node("fix", fix)
    g.add_node("reflect", reflect)
    g.add_edge("analyze", "fix")
    g.add_edge("fix", "reflect")
    g.add_conditional_edges("reflect", route, {"analyze": "analyze", "end": END})
    g.set_entry_point("analyze")
    return g.compile()


# ── STREAMLIT UI ──────────────────────────────────────────────

def main():
    """Main Streamlit app function."""

    # Initialise session state
    init_session_state()

    # ── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        st.title("🤖 CodePilot AI Studio")
        st.caption("Local AI · No internet · No API key")
        st.divider()

        # Model status indicator
        st.subheader("⚙️ Configuration")
        st.info(f"Model: **{MODEL_NAME}**\nRunning locally via Ollama")

        # Skill selector — manually choose skill
        st.subheader("🎯 Force Skill")
        forced_skill = st.selectbox(
            "Override auto-detection:",
            ["Auto-detect", "debug", "explain", "review"],
            help="Auto-detect reads your request to pick the right skill"
        )

        st.divider()

        # Architecture diagram
        st.subheader("🏗️ Architecture")
        st.markdown("""
```
Your Code
    ↓
Intent Router
    ↓
┌─────────────┐
│  debug()    │ ← Stage 3+5+6
│  explain()  │ ← Stage 3+4
│  review()   │ ← Stage 3+5
└─────────────┘
    ↓
Memory (Stage 2)
    ↓
Response
```
        """)

        # Clear memory button
        st.divider()
        if st.button("🗑️ Clear Conversation Memory"):
            st.session_state.messages = []
            st.session_state.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            st.success("Memory cleared!")

    # ── Main content area ─────────────────────────────────────
    st.title("🤖 CodePilot AI Studio")
    st.caption("Agentic AI Engineering Assistant · Built with Streamlit + LangChain + Ollama + ChromaDB")

    # ── Tabs — one per major feature ─────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 Debug / Explain / Review",
        "💬 Conversation Agent",
        "🕸️ LangGraph Workflow",
        "📚 Knowledge Base"
    ])

    # ── TAB 1: Main skills ────────────────────────────────────
    with tab1:
        st.header("Code Assistant")
        st.caption("Paste your Python code below and describe what you need.")

        # Code input area
        code_input = st.text_area(
            "Paste your Python code here:",
            height=200,
            placeholder="def my_function(x):\n    return x / 0  # something's wrong...",
            help="Paste any Python code — the agent will debug, explain, or review it"
        )

        # Request input
        request_input = st.text_input(
            "What do you need?",
            placeholder="e.g. 'debug this code' or 'explain what this does' or 'review my code'",
            help="Describe what you want. The agent will detect your intent automatically."
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            run_button = st.button("▶ Run Agent", type="primary", use_container_width=True)

        if run_button:
            if not code_input.strip():
                st.warning("Please paste some Python code first.")
            elif not request_input.strip():
                st.warning("Please describe what you need.")
            else:
                # Detect intent
                if forced_skill == "Auto-detect":
                    intent = detect_intent(request_input)
                else:
                    intent = forced_skill

                st.info(f"🧠 Detected intent: **{intent}**")

                # Load resources
                llm = load_llm()
                vectorstore = load_vectorstore()

                # Run the appropriate skill
                with st.spinner(f"Running {intent} skill..."):
                    if intent == "debug":
                        result = skill_debug(code_input, llm)
                        st.session_state.last_skill = "debug"
                    elif intent == "explain":
                        result = skill_explain(code_input, llm, vectorstore)
                        st.session_state.last_skill = "explain"
                    else:
                        result = skill_review(code_input, llm)
                        st.session_state.last_skill = "review"

                # Display result
                st.markdown("---")
                st.markdown(f"### 🤖 CodePilot Response ({intent}):")
                st.markdown(result)

                # Save to conversation history
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"[{intent}] {request_input}\n\nCode:\n```python\n{code_input}\n```"
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result
                })

    # ── TAB 2: Conversation Agent ─────────────────────────────
    with tab2:
        st.header("Conversation Agent (Memory)")
        st.caption("Chat with CodePilot. It remembers your full conversation.")

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input at the bottom
        if prompt := st.chat_input("Ask a coding question..."):
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate response using memory chain
            llm = load_llm()

            memory_prompt = PromptTemplate(
                input_variables=["chat_history", "input"],
                template="""You are CodePilot, an expert Python coding assistant.
You remember our full conversation.

Conversation so far:
{chat_history}

Student: {input}
CodePilot:"""
            )

            chain = ConversationChain(
                llm=llm,
                memory=st.session_state.memory,
                prompt=memory_prompt,
                verbose=False
            )

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chain.predict(input=prompt)
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

    # ── TAB 3: LangGraph Workflow ─────────────────────────────
    with tab3:
        st.header("LangGraph Debug Workflow")
        st.caption("Full stateful graph: Analyze → Fix → Reflect → (loop if needed)")

        graph_code = st.text_area(
            "Paste buggy code to run through the full graph:",
            height=150,
            placeholder="def buggy_function(x):\n    return 10 / x  # what if x is 0?"
        )

        if st.button("▶ Run LangGraph Workflow", type="primary"):
            if not graph_code.strip():
                st.warning("Please paste some Python code first.")
            else:
                llm = load_llm()
                app = build_debug_graph(llm)

                initial_state = {
                    "code": graph_code, "analysis": "",
                    "fix": "", "critique": "",
                    "iteration": 0, "approved": False, "final_output": ""
                }

                # Show progress as graph executes
                progress_placeholder = st.empty()
                result_placeholder = st.empty()

                with st.spinner("LangGraph executing..."):
                    final_state = None
                    node_log = []

                    for step in app.stream(initial_state):
                        node_name = list(step.keys())[0]
                        final_state = step[node_name]
                        node_log.append(f"✅ Completed node: **{node_name}** "
                                        f"(iteration {final_state.get('iteration', 0)})")
                        progress_placeholder.markdown("\n".join(node_log))

                # Show final result
                if final_state:
                    st.markdown("---")
                    st.markdown("### 🎯 Final Output:")
                    output = final_state.get("final_output") or final_state.get("fix", "")
                    st.markdown(output)

                    # Show graph stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Iterations", final_state.get("iteration", 0))
                    with col2:
                        st.metric("Approved", "Yes ✅" if final_state.get("approved") else "Max reached")

    # ── TAB 4: Knowledge Base ─────────────────────────────────
    with tab4:
        st.header("RAG Knowledge Base")
        st.caption("Search the ChromaDB knowledge base — see what the agent retrieves for any query.")

        search_query = st.text_input(
            "Search the knowledge base:",
            placeholder="e.g. 'IndexError', 'division by zero', 'list operations'"
        )

        if st.button("🔍 Search"):
            if search_query:
                vectorstore = load_vectorstore()
                retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

                with st.spinner("Searching..."):
                    results = retriever.invoke(search_query)

                st.markdown(f"**Found {len(results)} relevant chunks:**")
                for i, doc in enumerate(results):
                    with st.expander(f"Result {i+1}"):
                        st.text(doc.page_content)

        st.divider()
        st.subheader("📚 Knowledge Base Contents")
        st.caption(f"Stored at: `{DB_PATH}`")
        for i, knowledge in enumerate(PYTHON_KNOWLEDGE):
            with st.expander(f"Entry {i+1}: {knowledge[:50]}..."):
                st.text(knowledge)


# ── ENTRY POINT ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
