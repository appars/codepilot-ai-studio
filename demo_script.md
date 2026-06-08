# demo_script.md — Class Day Teaching Guide 🎓

> **Prof. Apparsamy Perumal** · Module 4 · 3-hour session

---

## Before Class Starts (15 min early)

```
□ Open Terminal 1 → run: ollama serve   (keep open all day)
□ Open Terminal 2 → activate venv, navigate to repo
□ Open Terminal 3 → have app_final/ ready to launch
□ Run: python setup_check.py → confirm 8/8 ✅
□ Open app_final in browser: streamlit run app.py
□ Have slides open on second screen
□ Write on whiteboard: git clone URL + setup_check.py command
```

---

## Block 1 — Concept Slides (0:00 – 0:40)

### 0:00 — Open with the Final App (5 min)
```
ACTION: Show the running app_final in browser
SAY:    "This is what we will understand today.
         A local AI coding assistant — no internet, no API key.
         Running entirely on this laptop.
         By the end of class, you will know how every part works."

DEMO:   Paste the buggy_sample.py code into the app
        Click debug → show the agent finding the bug
        Say: "Let's now understand how this is built — from scratch."
```

### 0:05 — Slide: LLM vs Agent (8 min)
```
KEY POINT: LLM = stateless. Agent = memory + tools + reflection.
ANALOGY:   LLM is like a person with amnesia.
           Agent is like a senior developer who remembers everything.
QUESTION:  "What would happen if your IDE forgot your code every time?"
```

### 0:13 — Slide: Memory Systems (8 min)
```
KEY POINT: Short-term = conversation buffer (lost on restart)
           Long-term = ChromaDB vector store (persists on disk)
ANALOGY:   Short-term = RAM. Long-term = hard drive.
DRAW:      User → Agent → Buffer Memory → Vector DB
QUESTION:  "Why can't we just store everything in short-term memory?"
           (answer: context window limit)
```

### 0:21 — Slide: Tool Orchestration (7 min)
```
KEY POINT: Agent detects intent → routes to the right skill
SHOW:      The 3 prompts (debug/explain/review) on screen
ANALOGY:   Like a hospital — you don't see a generic doctor.
           You see a specialist: cardiologist, neurologist, etc.
QUESTION:  "What other skills could a coding agent have?"
```

### 0:28 — Slide: Reflection + LangGraph (7 min)
```
KEY POINT: Reflection = agent critiques its own output
           LangGraph = graph with loops, not just linear chains
DRAW:      Generate → Critique → Improve → (approved?) → END
QUESTION:  "When you write code, do you review it yourself?
           Why should an AI be any different?"
```

### 0:35 — Pause for questions (5 min)
```
SAY:    "Any questions on the concepts before we see the code?"
        Clear all blockers NOW — harder to stop during demo.
ACTION: Ask students to open laptops and clone the repo.
        Write on board: git clone [URL]
        Ask them to run: python setup_check.py
```

---

## Block 2 — Live Demo on Your Mac (0:40 – 1:15)

> You run, students watch. Narrate every line out loud.

### 0:40 — Stage 1: Hello Ollama (10 min)
```
ACTION: cd stage1_hello_ollama
        Open run.py in your editor (font size 20+)

EXPLAIN line by line:
  from langchain_ollama import OllamaLLM
  → "This is the connector between Python and Ollama"

  llm = OllamaLLM(model="mistral")
  → "Like opening a phone call to the model"

  response = llm.invoke(prompt)
  → "This is the actual call — everything happens here"

ACTION: python run.py
PAUSE:  First run is slow — use this time to explain model loading
SAY:    "The model is loading into RAM — like opening a large app"

AFTER RESPONSE:
SAY:    "That response came from Mistral running on THIS laptop.
         No internet. No API key. Your data never left this machine."

QUESTION: "What would you change in the prompt to get a different answer?"
```

### 0:50 — Stage 2: Memory Agent (10 min)
```
ACTION: cd ../stage2_memory_agent
        Open run.py — point to ConversationBufferMemory

EXPLAIN:
  memory = ConversationBufferMemory(...)
  → "This is the notepad. Agent reads it before every reply."

  chain = ConversationChain(llm=..., memory=..., prompt=...)
  → "This is the glue that wires LLM + memory + prompt"

ACTION: Set verbose=True before running
        python run.py

POINT OUT: The full prompt shown in verbose mode — show {chat_history}
SAY:       "See how the agent gets the FULL conversation before every reply?
            That's how it remembers."

After Turn 3:
SAY:    "Turn 3 asks about 'the bug you just showed me'.
         It works because the agent read Turns 1 and 2 first."
```

### 1:00 — Stage 3: Tool Agent (10 min)
```
ACTION: cd ../stage3_tool_agent
        Open run.py — point to detect_intent()

EXPLAIN:
  debug_keywords = ["debug", "fix", "error", ...]
  → "Simple keyword matching — production systems use an LLM for this"

  def run_skill(intent, code):
  → "The dispatcher — picks the right prompt"

ACTION: python run.py
SAY:    "Same code, three different requests → three different outputs.
         This is tool orchestration."
```

### 1:10 — Show app_final (5 min)
```
ACTION: Switch to browser with app_final running
SAY:    "Now you've seen all the pieces. This app combines all of them."

DEMO:   Tab 1 → paste buggy_sample.py → click debug
        Tab 2 → have a short conversation
        Tab 3 → show LangGraph executing node by node
        Tab 4 → search knowledge base

SAY:    "Stages 4, 5, 6 power the RAG, reflection, and graph tabs.
         You'll explore those in the hands-on section and as homework."
```

---

## Block 3 — Students Hands-On (1:15 – 2:50)

### 1:15 — Setup check (10 min)
```
SAY:    "Run: python setup_check.py
         Everyone should see 8/8 checks pass.
         Raise your hand if any check fails."

ACTION: Walk around helping students with setup issues.
        Most common problem: venv not activated, Ollama not running.
```

### 1:25 — Stage 1 together (20 min)
```
SAY:    "Everyone open stage1_hello_ollama/run.py
         Read the comments at the top before running.
         Now run: python run.py"

WHILE THEY RUN:
  - Warn: "First run is slow — 30-60 seconds is normal"
  - Ask: "Who can explain to their neighbour what OllamaLLM does?"
  - Challenge fast finishers: "Try changing the prompt"

After all students have output:
  QUESTION: "Change MODEL_NAME to 'phi3:mini' — what changes?"
```

### 1:45 — Stage 2 independently (20 min)
```
SAY:    "Move to stage2_memory_agent
         Read the README first — Section 5 explains every line.
         Then run it. Your goal: understand what verbose=True shows."

CIRCULATE: Help students who are stuck.
           Most common issue: memory_key mismatch.

AFTER 15 min:
  QUESTION: "What is stored in memory after 3 turns?"
  SHOW:     The memory inspection output at the bottom.
```

### 2:05 — Stage 3 with experiments (20 min)
```
SAY:    "Stage 3 — run it, then try Experiment 1 from the README:
         Add a new 'optimize' skill.
         You have 20 minutes. Work in pairs if you like."

CHALLENGE for fast students:
  "Can you make the intent router use an LLM instead of keywords?
   Hint: README Experiment 3"
```

### 2:25 — Free exploration (25 min)
```
SAY:    "For the remaining time:
         - Fast finishers: try Stage 4 (RAG) — README is detailed
         - Others: run app_final, explore the 4 tabs
         - Everyone: read the Stage 5 README — it's good homework"

ACTION: Circulate. Answer questions. Encourage experimentation.
```

---

## Block 4 — Wrap Up (2:50 – 3:00)

### 2:50 — Summary (5 min)
```
SAY:    "What did we cover today?"
DRAW:   The architecture on the board:
        Ollama → LangChain → Memory → Tools → Reflection → LangGraph

"Stage 1: Local LLM — no cloud needed"
"Stage 2: Memory — agent remembers your conversation"
"Stage 3: Tools — agent routes to the right skill"
"Stage 4, 5, 6 — homework — RAG, reflection, LangGraph"
```

### 2:55 — Homework (3 min)
```
ASSIGN:
  1. Complete Stages 4, 5, 6 — run each and read the README
  2. Add a new skill to Stage 3: refactor() or optimize()
  3. Try the Experiment sections at the bottom of each run.py
  4. Stage 6 bonus: add a documentation_node to the LangGraph

OPTIONAL CHALLENGE:
  "Take app_final and add a 4th skill of your own design.
   What would you want a coding assistant to do that it doesn't do yet?"
```

### 2:58 — Final thought (2 min)
```
SAY:    "The future software engineer will not compete with AI.
         They will collaborate with AI agents.
         You just built one. From scratch. On your own laptop.
         That is a significant achievement."
```

---

## Emergency Fallbacks

### If Ollama crashes during demo
```bash
pkill ollama && ollama serve
# Takes ~30 seconds to restart
# Use the time to ask a concept question to the class
```

### If a student's laptop can't run Mistral (4GB RAM)
```
Change MODEL_NAME = "phi3:mini" in run.py
Run: ollama pull phi3:mini
Quality is slightly lower but all concepts still work
```

### If Stage 4 RAG is too slow in class
```
Skip it during hands-on — assign as homework
The Stage 3 concepts (tools + routing) are more important for the 3-hour session
```

### If students finish all 3 stages early
```
Show them: cd app_final && streamlit run app.py
Challenge: "Find a Python bug online. Paste it into the debug tab.
            Does the agent fix it correctly? When does it fail?"
```
