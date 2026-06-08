# ============================================================
# preload.py — Run this the night before class!
# ============================================================
# This script downloads everything needed for offline use.
# Run it once on home WiFi — never need internet in class.
#
# What it downloads:
#   1. Mistral model via Ollama (~4GB)
#   2. HuggingFace embedding model (~90MB)
#
# Run this script:
#   python preload.py
#
# Time needed: 10-30 minutes depending on internet speed
# ============================================================

import subprocess   # to run ollama pull command
import sys          # for exit codes

print("=" * 60)
print("CodePilot AI Studio — Pre-Class Setup")
print("=" * 60)
print("This downloads everything needed for offline class use.")
print("Run this ONCE at home on WiFi — not in class!")
print()

# ── Step 1: Download Mistral via Ollama ──────────────────────
print("Step 1/2: Downloading Mistral model (~4GB)...")
print("This may take 10-30 minutes on first run.")
print()

try:
    # Run ollama pull — this downloads the model
    result = subprocess.run(
        ["ollama", "pull", "mistral"],
        check=True,             # raise error if command fails
        capture_output=False    # show progress in terminal
    )
    print("\n✅ Mistral downloaded successfully!")
except subprocess.CalledProcessError:
    print("\n❌ Failed to download Mistral.")
    print("   Make sure Ollama is installed and running.")
    print("   Mac: brew install ollama && ollama serve")
    print("   Windows: Download from https://ollama.com")
    sys.exit(1)
except FileNotFoundError:
    print("\n❌ Ollama not found.")
    print("   Install Ollama first:")
    print("   Mac: brew install ollama")
    print("   Windows: Download OllamaSetup.exe from https://ollama.com")
    sys.exit(1)

# Also pull phi3:mini as a fallback for low-RAM laptops
print("\nAlso downloading phi3:mini as fallback for 4GB RAM laptops...")
try:
    subprocess.run(["ollama", "pull", "phi3:mini"], check=True)
    print("✅ phi3:mini downloaded!")
except Exception:
    print("⚠️  phi3:mini download failed — not critical, mistral is the main model")

print()

# ── Step 2: Download HuggingFace embedding model ─────────────
print("Step 2/2: Downloading HuggingFace embedding model (~90MB)...")
print("This is cached locally and works offline after download.")
print()

try:
    # Importing and initialising the embeddings triggers the download
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Test that it works by embedding a sample sentence
    test_vector = embeddings.embed_query("Python IndexError test")
    print(f"✅ Embedding model loaded! Vector size: {len(test_vector)} dimensions")

except ImportError:
    print("❌ langchain-huggingface not installed.")
    print("   Run: pip install langchain-huggingface sentence-transformers")
    sys.exit(1)
except Exception as e:
    print(f"❌ Embedding model download failed: {e}")
    sys.exit(1)

# ── Summary ───────────────────────────────────────────────────
print()
print("=" * 60)
print("✅ All downloads complete! You are ready for class.")
print("=" * 60)
print()
print("What was downloaded:")
print("  ✓ Mistral 7B model (via Ollama)")
print("  ✓ phi3:mini model (fallback for low RAM)")
print("  ✓ all-MiniLM-L6-v2 embeddings (for RAG)")
print()
print("In class, run setup_check.py to verify everything works:")
print("  python setup_check.py")
