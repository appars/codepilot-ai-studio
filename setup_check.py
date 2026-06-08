# ============================================================
# setup_check.py — Run this at the START of class
# ============================================================
# Verifies that every component of CodePilot is working.
# Run before teaching starts so problems surface early.
#
# Run this script:
#   python setup_check.py
#
# Green ✅ = ready to use
# Red   ❌ = fix before proceeding
# Yellow ⚠️ = warning, may still work
# ============================================================

import sys
import subprocess
import importlib

# Track overall pass/fail
results = []

def check(name, test_fn):
    """Run a check and record the result."""
    try:
        message = test_fn()
        print(f"  ✅ {name}: {message}")
        results.append((name, True))
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        results.append((name, False))

print("=" * 60)
print("CodePilot AI Studio — Setup Verification")
print("=" * 60)
print()

# ── CHECK 1: Python version ───────────────────────────────────
print("Checking Python...")
check("Python version", lambda: (
    f"{sys.version_info.major}.{sys.version_info.minor} ✓"
    if sys.version_info >= (3, 9)
    else (_ for _ in ()).throw(Exception(f"Need Python 3.9+, got {sys.version_info.major}.{sys.version_info.minor}"))
))
print()

# ── CHECK 2: Required Python packages ────────────────────────
print("Checking Python packages...")
packages = [
    ("streamlit",              "streamlit"),
    ("langchain",              "langchain"),
    ("langchain_ollama",       "langchain-ollama"),
    ("langchain_community",    "langchain-community"),
    ("langchain_huggingface",  "langchain-huggingface"),
    ("langchain_chroma",       "langchain-chroma"),
    ("langgraph",              "langgraph"),
    ("chromadb",               "chromadb"),
    ("sentence_transformers",  "sentence-transformers"),
]

for import_name, package_name in packages:
    def make_check(imp, pkg):
        def fn():
            importlib.import_module(imp)
            return f"installed"
        return fn
    check(package_name, make_check(import_name, package_name))
print()

# ── CHECK 3: Ollama is running ────────────────────────────────
print("Checking Ollama...")
import urllib.request

def check_ollama():
    try:
        response = urllib.request.urlopen("http://localhost:11434", timeout=3)
        return "running on port 11434"
    except Exception:
        raise Exception(
            "Ollama not running!\n"
            "    Mac: run 'ollama serve' in a terminal\n"
            "    Windows: start Ollama from Start Menu"
        )

check("Ollama service", check_ollama)

# ── CHECK 4: Mistral model available ─────────────────────────
def check_mistral():
    import json
    try:
        response = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        data = json.loads(response.read())
        models = [m["name"] for m in data.get("models", [])]
        mistral_found = any("mistral" in m for m in models)
        phi3_found    = any("phi3" in m for m in models)

        if mistral_found:
            return "mistral available"
        elif phi3_found:
            return "⚠️  Only phi3:mini found (low RAM mode)"
        else:
            raise Exception("No models found! Run: ollama pull mistral")
    except urllib.error.URLError:
        raise Exception("Cannot connect to Ollama — is it running?")

check("Mistral model", check_mistral)
print()

# ── CHECK 5: HuggingFace embeddings ──────────────────────────
print("Checking embeddings...")

def check_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    emb = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    vec = emb.embed_query("test")
    return f"working, vector size={len(vec)}"

check("HuggingFace all-MiniLM-L6-v2", check_embeddings)
print()

# ── CHECK 6: Quick LLM test ───────────────────────────────────
print("Checking LLM response (quick test)...")

def check_llm():
    from langchain_ollama import OllamaLLM
    llm = OllamaLLM(model="mistral", temperature=0)
    response = llm.invoke("Reply with exactly: CODEPILOT_OK")
    if "CODEPILOT" in response.upper() or len(response) > 0:
        return f"responding ({len(response)} chars)"
    raise Exception("Model responded but with unexpected output")

check("Ollama LLM response", check_llm)
print()

# ── CHECK 7: ChromaDB write ───────────────────────────────────
print("Checking ChromaDB...")

def check_chromadb():
    import chromadb
    import pathlib
    import tempfile

    # Test write to a temp directory
    with tempfile.TemporaryDirectory() as tmp:
        client = chromadb.PersistentClient(path=tmp)
        col = client.create_collection("test")
        col.add(documents=["test doc"], ids=["1"])
        result = col.query(query_texts=["test"], n_results=1)
        if result["documents"]:
            return "read/write working"
    raise Exception("ChromaDB test failed")

check("ChromaDB read/write", check_chromadb)
print()

# ── SUMMARY ──────────────────────────────────────────────────
passed = sum(1 for _, ok in results if ok)
total  = len(results)
failed = [(name, ok) for name, ok in results if not ok]

print("=" * 60)
print(f"RESULT: {passed}/{total} checks passed")
print("=" * 60)

if not failed:
    print()
    print("🎉 Everything is working! You are ready for class.")
    print()
    print("Quick start:")
    print("  Stage 1: cd stage1_hello_ollama && python run.py")
    print("  Final app: cd app_final && streamlit run app.py")
else:
    print()
    print("❌ Fix these before class:")
    for name, _ in failed:
        print(f"   • {name}")
    print()
    print("See SETUP_MAC.md or SETUP_WINDOWS.md for fix instructions.")
    sys.exit(1)
