# ============================================================
# CodePilot AI Studio — Stage 4: RAG Explain
# ============================================================
# Concept  : Long-term memory using RAG (Retrieval Augmented Generation)
# Framework: LangChain + ChromaDB + HuggingFace Embeddings + Ollama
# Model    : Mistral (local) + all-MiniLM-L6-v2 (local embeddings)
#
# What you will learn:
#   - What RAG is and why it is powerful
#   - What vector embeddings are (numbers that represent meaning)
#   - How ChromaDB stores and retrieves knowledge semantically
#   - How to build a knowledge base from text documents
#   - How to augment LLM responses with retrieved context
#
# The problem we are solving:
#   Short-term memory (Stage 2) is lost when the program restarts.
#   RAG gives the agent PERSISTENT knowledge — a knowledge base
#   that survives restarts and grows over time.
#   When explaining code, the agent retrieves relevant Python
#   concepts BEFORE generating its explanation.
#
# How RAG works:
#   1. BUILD: Store knowledge as vector embeddings in ChromaDB
#   2. RETRIEVE: Find most relevant knowledge for the user's query
#   3. AUGMENT: Add retrieved context to the prompt
#   4. GENERATE: LLM produces a better answer using the context
#
# Run this file:
#   python run.py
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
from langchain_ollama import OllamaLLM                          # local LLM
from langchain_huggingface import HuggingFaceEmbeddings          # converts text to vectors
from langchain_chroma import Chroma                              # vector database
from langchain.text_splitter import RecursiveCharacterTextSplitter  # splits long text
from langchain.prompts import PromptTemplate                     # prompt formatting
import pathlib                                                   # cross-platform paths
import os                                                        # file system operations

# ── STEP 1: Connect to local LLM ─────────────────────────────
llm = OllamaLLM(model="mistral", temperature=0.3)

# ── STEP 2: Set up local embeddings ──────────────────────────
# Embeddings convert text into vectors (lists of numbers).
# Similar meanings produce similar vectors.
# Example: "bug" and "error" will have similar vectors.
# Example: "bug" and "banana" will have very different vectors.
#
# all-MiniLM-L6-v2:
#   - Small model (~90MB) — downloads once, works offline forever
#   - Fast enough for classroom use
#   - Good enough for code-related similarity searches
#   - Stored in ~/.cache/huggingface after first download
print("Loading embedding model (downloading if first time, ~90MB)...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",        # the embedding model to use
    model_kwargs={"device": "cpu"},         # use CPU (no GPU needed)
    encode_kwargs={"normalize_embeddings": True}  # normalise for better similarity
)
print("✅ Embedding model loaded.")

# ── STEP 3: Define our Python knowledge base ─────────────────
# This is the knowledge we want the agent to retrieve from.
# In a real system, this would be loaded from files, docs, or a database.
# We define it inline here for simplicity.
#
# Each entry is a piece of knowledge about a Python concept.
# ChromaDB will store these as vectors and find relevant ones
# when a user asks about code.

PYTHON_KNOWLEDGE = [
    """IndexError in Python:
An IndexError occurs when you try to access a list, tuple, or string
using an index that is out of range.
Example: my_list = [1, 2, 3]; my_list[5] raises IndexError.
Fix: Always check len() before accessing by index, or use try/except.""",

    """ZeroDivisionError in Python:
A ZeroDivisionError occurs when you divide a number by zero.
Example: result = 10 / 0 raises ZeroDivisionError.
Fix: Always check if the denominator is zero before dividing.
Use: if divisor != 0: result = numerator / divisor""",

    """TypeError in Python:
A TypeError occurs when an operation is applied to an object of inappropriate type.
Example: result = "hello" + 5 raises TypeError.
Fix: Use type conversion: result = "hello" + str(5)
Or check types with isinstance() before performing operations.""",

    """Python Functions Best Practices:
Functions should do ONE thing and do it well (Single Responsibility Principle).
Always add docstrings to explain what a function does.
Use meaningful parameter names.
Handle edge cases like empty inputs or None values.
Return consistent types — don't return int sometimes and None other times.""",

    """Python List Operations:
Common list methods: append(), extend(), insert(), remove(), pop(), sort(), reverse().
List comprehensions are more Pythonic than loops for creating lists.
Use enumerate() when you need both index and value.
Use zip() to iterate over multiple lists simultaneously.
Always check if a list is empty before accessing elements.""",

    """Python Exception Handling:
Use try/except to handle errors gracefully.
Catch specific exceptions, not bare except.
Use finally for cleanup code that must always run.
Raise exceptions with helpful error messages.
Example structure:
try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except ZeroDivisionError:
    print("Cannot divide by zero")
finally:
    cleanup()""",
]

# ── STEP 4: Build the vector knowledge base ───────────────────
# We store the knowledge in ChromaDB (a local vector database).
# ChromaDB saves to disk — so it persists across program restarts!
#
# persist_directory: where ChromaDB saves data on your computer
# collection_name: like a table name in a regular database

DB_PATH = pathlib.Path(__file__).parent / "knowledge_db"  # local folder

# Check if knowledge base already exists to avoid rebuilding every run
if DB_PATH.exists() and any(DB_PATH.iterdir()):
    # Load existing knowledge base from disk
    print("📚 Loading existing knowledge base from disk...")
    vectorstore = Chroma(
        collection_name="python_knowledge",
        embedding_function=embeddings,       # must use same embeddings as when built
        persist_directory=str(DB_PATH)       # where the data is stored
    )
    print(f"✅ Loaded knowledge base with existing documents.")
else:
    # Build knowledge base from scratch and save to disk
    print("🔨 Building knowledge base (first time only)...")

    # Split long documents into chunks for better retrieval
    # Large chunks might contain irrelevant info mixed with relevant info
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # max characters per chunk
        chunk_overlap=50     # overlap between chunks to avoid cutting context
    )
    chunks = splitter.create_documents(PYTHON_KNOWLEDGE)

    # Create ChromaDB and store all chunks as vectors
    vectorstore = Chroma.from_documents(
        documents=chunks,                      # the text chunks to store
        embedding=embeddings,                  # how to convert text to vectors
        collection_name="python_knowledge",    # name of this collection
        persist_directory=str(DB_PATH)         # save to disk
    )
    print(f"✅ Knowledge base built with {len(chunks)} chunks. Saved to {DB_PATH}")

# ── STEP 5: Create a retriever ────────────────────────────────
# The retriever is the interface for searching the knowledge base.
# search_type="similarity" finds the most semantically similar chunks.
# k=2 means retrieve the top 2 most relevant chunks.
retriever = vectorstore.as_retriever(
    search_type="similarity",   # find semantically similar content
    search_kwargs={"k": 2}      # retrieve top 2 most relevant chunks
)

# ── STEP 6: Define the RAG explain prompt ─────────────────────
# This prompt includes {context} — the retrieved knowledge.
# The LLM uses this context to give a more informed explanation.
RAG_EXPLAIN_PROMPT = PromptTemplate(
    input_variables=["context", "code"],
    template="""You are a Python tutor with access to a knowledge base.
Use the relevant knowledge below to give a thorough explanation.

RELEVANT KNOWLEDGE FROM KNOWLEDGE BASE:
{context}

Now explain the following Python code using the knowledge above:
```python
{code}
```

Your explanation should:
1. WHAT IT DOES: One sentence summary
2. HOW IT WORKS: Step by step walkthrough
3. POTENTIAL ISSUES: Any bugs or risks (use the knowledge base)
4. BEGINNER TIP: One practical advice for students

Be clear and reference the knowledge base where relevant."""
)

# ── STEP 7: The RAG pipeline function ────────────────────────
def rag_explain(code: str) -> str:
    """
    Explain code using RAG:
    1. Convert code to a search query
    2. Retrieve relevant knowledge from ChromaDB
    3. Combine knowledge + code into a prompt
    4. Generate explanation with Mistral

    Args:
        code: Python code to explain

    Returns:
        Detailed explanation string
    """
    # Step 7a: Create a search query from the code
    # We ask what concepts the code uses — this finds relevant knowledge
    search_query = f"Python concepts and potential errors in this code: {code[:200]}"

    # Step 7b: Retrieve relevant knowledge chunks
    # ChromaDB converts the query to a vector and finds similar stored vectors
    relevant_docs = retriever.invoke(search_query)

    # Step 7c: Combine retrieved chunks into a single context string
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Step 7d: Format the prompt with context + code
    prompt = RAG_EXPLAIN_PROMPT.format(context=context, code=code)

    # Step 7e: Generate explanation with Mistral
    return llm.invoke(prompt)


# ── STEP 8: Demo the RAG pipeline ────────────────────────────
def main():
    print("=" * 60)
    print("CodePilot AI Studio — Stage 4: RAG Explain")
    print("=" * 60)
    print()

    # Sample code with multiple potential issues
    sample_code = """
def get_first_element(my_list):
    return my_list[0]

def calculate_ratio(a, b):
    return a / b

numbers = [10, 20, 30]
print(get_first_element(numbers))
print(get_first_element([]))     # will this crash?
print(calculate_ratio(10, 0))   # what about this?
"""

    print("Code to explain:")
    print(sample_code)
    print("-" * 60)
    print("🔍 Searching knowledge base for relevant concepts...")

    # Show what was retrieved — great for teaching!
    search_query = f"Python concepts and errors: {sample_code[:200]}"
    retrieved = retriever.invoke(search_query)
    print(f"📚 Retrieved {len(retrieved)} relevant chunks:")
    for i, doc in enumerate(retrieved):
        print(f"  [{i+1}] {doc.page_content[:80]}...")
    print()
    print("🤖 Generating RAG-enhanced explanation...")
    print("-" * 60)

    explanation = rag_explain(sample_code)
    print(explanation)

    print()
    print("=" * 60)
    print("✅ Stage 4 complete! RAG is working.")
    print()
    print("KEY INSIGHT: The agent retrieved relevant Python knowledge")
    print("BEFORE generating the explanation. This is RAG.")
    print(f"Knowledge base is stored at: {DB_PATH}")
    print("It persists across program restarts — this is long-term memory!")


if __name__ == "__main__":
    main()

# ── TRY THIS ─────────────────────────────────────────────────
# 1. Add a new document to PYTHON_KNOWLEDGE — delete the DB folder
#    and run again to rebuild with your new knowledge
# 2. Change k=2 to k=4 — does more context improve the explanation?
# 3. Print the raw vectors: print(embeddings.embed_query("IndexError"))
#    Can you see how similar texts produce similar numbers?
# 4. Add your own code snippet — does it retrieve relevant knowledge?
