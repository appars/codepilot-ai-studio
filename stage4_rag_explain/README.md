# Stage 4 — RAG Explain 📚

> **Concept:** Long-term memory using RAG (Retrieval Augmented Generation) with ChromaDB and local HuggingFace embeddings.

---

## 1. What You Will Learn

By the end of this stage you will understand:

- What **RAG** is and why it is one of the most important patterns in AI
- What **vector embeddings** are — how text becomes numbers that encode meaning
- How **ChromaDB** stores knowledge and finds relevant content by meaning, not keywords
- How to build a **persistent knowledge base** that survives program restarts
- How to **augment** an LLM's answer with retrieved knowledge

### The Big Idea

```
WITHOUT RAG:                        WITH RAG:
                                    ┌─────────────────────┐
                                    │   Knowledge Base     │
                                    │  (ChromaDB on disk)  │
User asks about code                └──────────┬──────────┘
        ↓                                      │ retrieve
   Mistral answers               User asks → Retriever → finds relevant
   from training                              ↓            knowledge
   data only                             Mistral answers
   (may be vague)                        WITH context
                                         (much better!)
```

**RAG = Give the LLM the right textbook page before asking the question.**

---

## 2. How It Works

### Step 1 — Embed and Store (done once)

```
"IndexError occurs when index is out of range..."
                    ↓
          HuggingFace Embeddings
          (all-MiniLM-L6-v2)
                    ↓
    [0.23, -0.45, 0.87, 0.12, ...]   ← 384 numbers
                    ↓
              ChromaDB stores
         (text + vector + metadata)
```

### Step 2 — Retrieve (every query)

```
User's code: "my_list[5]"
                    ↓
          Convert to vector
    [0.21, -0.41, 0.89, 0.15, ...]
                    ↓
     ChromaDB finds most similar
          stored vectors
                    ↓
    Returns: "IndexError occurs when
              index is out of range..."
```

### Step 3 — Augment and Generate

```
prompt = """
RELEVANT KNOWLEDGE:
IndexError occurs when index is out of range...
ZeroDivisionError occurs when dividing by zero...

Now explain this code:
my_list[5]  ← retriever found this is relevant
"""
        ↓
     Mistral generates a knowledge-backed explanation
```

### Why ChromaDB?

- Runs **100% locally** — no cloud, no API key
- Data **persists on disk** — survives program restarts
- Searches by **semantic meaning**, not just keywords
- "bug" and "error" are similar → retrieves both even if you only search for one

---

## 3. Setup and Run Commands

> ⚠️ **Run `preload.py` from the repo root before class** to download the embedding model (~90MB)

On Mac:
```bash
cd stage4_rag_explain
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

On Windows:
```bash
cd stage4_rag_explain
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**First run:** Downloads and caches `all-MiniLM-L6-v2` (~90MB).  
**All later runs:** Loads from cache — instant, no internet needed.

---

## 4. Expected Output

```
Loading embedding model (downloading if first time)...
✅ Embedding model loaded.
🔨 Building knowledge base (first time only)...
✅ Knowledge base built with 8 chunks. Saved to knowledge_db/

============================================================
CodePilot AI Studio — Stage 4: RAG Explain
============================================================

Code to explain: [sample code shown here]

🔍 Searching knowledge base for relevant concepts...
📚 Retrieved 2 relevant chunks:
  [1] IndexError in Python: An IndexError occurs when you try...
  [2] Python Functions Best Practices: Functions should do ONE...

🤖 Generating RAG-enhanced explanation...
------------------------------------------------------------
1. WHAT IT DOES: Defines two functions that access list elements
   and divide numbers, then calls them with edge-case inputs.

2. HOW IT WORKS: get_first_element() returns index 0 of a list.
   calculate_ratio() divides two numbers. Both are called with
   inputs that will trigger errors.

3. POTENTIAL ISSUES:
   - get_first_element([]) will raise IndexError (from knowledge base:
     IndexError occurs when index is out of range)
   - calculate_ratio(10, 0) will raise ZeroDivisionError

4. BEGINNER TIP: Always handle edge cases — empty lists and
   zero denominators are the most common sources of crashes.
```

On the **second run**, the knowledge base loads from disk instantly — no rebuild needed.

---

## 5. Code Walkthrough

### Setting Up Embeddings
```python
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
```
This loads a small, fast embedding model that runs entirely on your CPU.  
`normalize_embeddings=True` makes similarity scores consistent (between 0 and 1).

### Building the Knowledge Base
```python
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="python_knowledge",
    persist_directory=str(DB_PATH)   # saves to disk!
)
```
`persist_directory` is the key — this makes ChromaDB save to your hard drive.  
Without it, data is lost when the program ends (like short-term memory).

### Loading Existing Knowledge Base
```python
if DB_PATH.exists() and any(DB_PATH.iterdir()):
    vectorstore = Chroma(
        collection_name="python_knowledge",
        embedding_function=embeddings,
        persist_directory=str(DB_PATH)
    )
```
On subsequent runs, we skip rebuilding and just load from disk.  
This is what makes RAG feel like "long-term memory".

### The Retriever
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)
```
`k=2` means fetch the 2 most relevant chunks.  
More chunks = more context but slower and risks irrelevant content.

### The RAG Pipeline
```python
def rag_explain(code: str) -> str:
    relevant_docs = retriever.invoke(search_query)         # Step 1: Retrieve
    context = "\n\n".join([doc.page_content for doc in relevant_docs])  # Step 2: Combine
    prompt = RAG_EXPLAIN_PROMPT.format(context=context, code=code)      # Step 3: Augment
    return llm.invoke(prompt)                                            # Step 4: Generate
```
Four lines. That is the entire RAG pipeline. Simple but powerful.

---

## 6. Common Errors and Fixes

### ❌ `ModuleNotFoundError: No module named 'chromadb'`
**Fix:** `pip install -r requirements.txt` (with venv active)

### ❌ Embedding model download fails / very slow
**Cause:** No internet or slow connection.  
**Fix:** Run `preload.py` from repo root on home WiFi the night before class.

### ❌ `RuntimeError: no such collection`
**Cause:** ChromaDB folder exists but is corrupted or from a different run.  
**Fix:** Delete the `knowledge_db/` folder and run again — it will rebuild.

### ❌ On Windows: `OSError: [Errno 22]` when saving ChromaDB
**Cause:** Path contains spaces or special characters.  
**Fix:** We use `pathlib.Path` which handles Windows paths correctly. Make sure you cloned the repo to a path without spaces (e.g. `C:\codepilot` not `C:\My Documents\codepilot`).

### ❌ Retrieval returns irrelevant chunks
**Cause:** Knowledge base doesn't have relevant content for the code.  
**Fix:** Add more documents to `PYTHON_KNOWLEDGE` that match your code topics.

---

## 7. Try It Yourself

**Experiment 1 — See the raw vectors**
```python
vector = embeddings.embed_query("IndexError")
print(f"Vector has {len(vector)} dimensions")
print(f"First 5 values: {vector[:5]}")
```
Notice: 384 numbers represent the meaning of "IndexError".

**Experiment 2 — Test semantic similarity**
```python
# These should retrieve similar results even though words differ
results1 = retriever.invoke("list index out of bounds")
results2 = retriever.invoke("IndexError in Python")
# Both should find the IndexError knowledge chunk
print(results1[0].page_content)
print(results2[0].page_content)
```

**Experiment 3 — Add your own knowledge**
Add a new entry to `PYTHON_KNOWLEDGE`:
```python
"""Python Recursion:
Recursion is when a function calls itself.
Always define a base case to stop the recursion.
Without a base case, you get RecursionError: maximum recursion depth exceeded.
Example: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"""
```
Delete `knowledge_db/` folder and run again. Now ask about recursive code!

**Experiment 4 — Increase retrieved chunks**
Change `k=2` to `k=4` in the retriever.  
Does having more context improve the explanation?  
What is the trade-off?

---

## Key Concepts Summary

| Concept | What it means |
|---------|--------------|
| RAG | Retrieve relevant knowledge, then generate with context |
| Embedding | Converting text to a vector of numbers that encode meaning |
| Vector similarity | Finding text with similar meaning by comparing vectors |
| ChromaDB | Local vector database — stores and searches embeddings |
| `persist_directory` | Saves ChromaDB to disk for long-term memory |
| Retriever | Interface for searching the vector store |
| `k` | Number of chunks to retrieve (top-k most similar) |

---

## What's Next?

In **Stage 5** we add **reflection loops** — the agent critiques its own output and improves it.  
This is what makes the difference between a basic AI assistant and a self-improving one.

➡️ Move to [`../stage5_reflection_review/`](../stage5_reflection_review/README.md)
