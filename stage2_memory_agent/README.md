# Stage 2 — Memory Agent 🧠

> **Concept:** Short-term memory — the agent remembers your full conversation, not just the last message.

---

## 1. What You Will Learn

By the end of this stage you will understand:

- Why a stateless LLM is like **a person with amnesia** — forgets everything after each reply
- What **short-term memory** means for an AI agent
- How `ConversationBufferMemory` stores and replays chat history
- How a `PromptTemplate` injects memory into every LLM call
- How `ConversationChain` wires the LLM + memory + prompt together

### The Problem We Are Solving

```
WITHOUT memory (Stage 1):           WITH memory (Stage 2):

Turn 1: "What is IndexError?"       Turn 1: "What is IndexError?"
→ Agent: "It means index out of     → Agent: "It means index out of
          range..."                            range..."

Turn 2: "Show me an example"        Turn 2: "Show me an example"
→ Agent: "Example of WHAT?"  ❌     → Agent: "Sure! Here is an
         (forgot Turn 1)                       IndexError example..." ✅
                                               (remembered Turn 1)
```

---

## 2. How It Works

### The Memory Mechanism

```
Every time the agent replies, this happens:

User input ──────────────────────────────────┐
                                             ↓
Memory loads history ──► PromptTemplate ──► LLM ──► Response
                          fills in:                      │
                          {chat_history}                 │
                          {input}                        ↓
                                             Memory saves new exchange
```

### What ConversationBufferMemory actually stores

```python
# After 2 turns, memory contains:
[
  HumanMessage(content="What is IndexError?"),
  AIMessage(content="IndexError means..."),
  HumanMessage(content="Show me an example"),
  AIMessage(content="Here is an example...")
]
```

The agent reads this ENTIRE list before generating every new response.  
That is how it "remembers" — it re-reads the conversation history every time.

### The Prompt Template with Memory

```
You are CodePilot, a helpful Python coding assistant.

Conversation so far:
Human: What is IndexError?
AI: IndexError means index out of range...
Human: Show me an example
AI: Here is an example: mylist = [1,2,3]; print(mylist[5])...

Student: How do I fix it?     ← current question
CodePilot:                     ← model generates here
```

---

## 3. Setup and Run Commands

**Make sure Ollama is running first** (see Stage 1 README)

On Mac:
```bash
cd stage2_memory_agent
source ../stage1_hello_ollama/venv/bin/activate   # reuse Stage 1 venv
# OR create a new one:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

On Windows:
```bash
cd stage2_memory_agent
..\stage1_hello_ollama\venv\Scripts\activate   # reuse Stage 1 venv
# OR create a new one:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

## 4. Expected Output

```
============================================================
CodePilot AI Studio — Stage 2: Memory Agent
============================================================
Demonstrating short-term memory across multiple turns...

👤 Student: What is an IndexError in Python?
🤖 CodePilot: An IndexError occurs when you try to access a list
              element using an index that doesn't exist...

👤 Student: Can you give me a simple code example of that error?
🤖 CodePilot: Sure! Here's the example we discussed:
              my_list = [1, 2, 3]
              print(my_list[5])  # IndexError: list index out of range
              ...

👤 Student: How do I fix the bug you just showed me?
🤖 CodePilot: To fix the IndexError I showed you, you can...

------------------------------------------------------------
📦 What is stored in memory right now?
------------------------------------------------------------
[1] 👤 Student: What is an IndexError in Python?...
[2] 🤖 CodePilot: An IndexError occurs when you try to access...
[3] 👤 Student: Can you give me a simple code example...
[4] 🤖 CodePilot: Sure! Here's the example we discussed...
[5] 👤 Student: How do I fix the bug you just showed me?...
[6] 🤖 CodePilot: To fix the IndexError I showed you...

Total messages in memory: 6
============================================================
✅ Stage 2 complete! Memory is working.
```

---

## 5. Code Walkthrough

### The Memory Object
```python
memory = ConversationBufferMemory(
    memory_key="chat_history",   # variable name in prompt template
    return_messages=True          # store as objects, not raw text
)
```
`memory_key` must **exactly match** the `{chat_history}` variable in the prompt template.  
If these don't match, memory won't be injected and the agent will seem to forget everything.

### The Prompt Template
```python
prompt_template = PromptTemplate(
    input_variables=["chat_history", "input"],
    template="""...{chat_history}...{input}..."""
)
```
`input_variables` tells LangChain which `{placeholder}` variables to fill in.  
Every time `chain.predict()` is called, LangChain automatically:
1. Reads memory and fills `{chat_history}`
2. Takes your new message and fills `{input}`
3. Sends the complete filled-in prompt to the LLM

### The Conversation Chain
```python
chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt_template,
    verbose=False    # change to True to see the full prompt!
)
```
`ConversationChain` is the glue that connects all three parts.  
After every `chain.predict()` call, it automatically saves both the question and answer to memory.

### Making a call
```python
response = chain.predict(input="your question here")
```
This one line does 5 things automatically:
1. Loads history from memory
2. Fills in the prompt template
3. Sends to Mistral
4. Gets the response
5. Saves question + answer back to memory

---

## 6. Common Errors and Fixes

### ❌ `ValueError: Missing keys in input`
**Cause:** The `memory_key` in `ConversationBufferMemory` doesn't match the `{variable}` in the prompt template.  
**Fix:** Make sure `memory_key="chat_history"` and `{chat_history}` in the template are identical.

### ❌ Agent doesn't seem to remember previous messages
**Cause:** `verbose=False` hides what's happening — the memory might be working but not obvious.  
**Fix:** Set `verbose=True` and run again. You will see the full prompt with history injected.

### ❌ `ImportError: cannot import name 'ConversationChain'`
**Cause:** Wrong version of LangChain installed.  
**Fix:** Run `pip install -r requirements.txt` again with the venv active.

### ❌ Responses are repetitive or generic
**Cause:** The prompt template is not specific enough.  
**Fix:** Add more context to the system part of the template — tell the agent exactly what role to play.

---

## 7. Try It Yourself

**Experiment 1 — See the full prompt**  
Change `verbose=False` to `verbose=True` in the `ConversationChain`.  
Run again. You will see the exact prompt (with memory injected) that gets sent to Mistral.  
This is the best way to understand how memory really works.

**Experiment 2 — Test memory limits**  
Add more turns to the conversation (Turn 4, Turn 5, Turn 6...).  
At what point does the context window fill up?  
Try asking "what was my first question?" after 10 turns.

**Experiment 3 — Clear the memory**  
Add this line after Turn 3:
```python
memory.clear()
print("Memory cleared!")
response4 = chain.predict(input="What were we just talking about?")
print(response4)  # should say it doesn't know — memory is gone
```

**Experiment 4 — Change buffer size**  
Replace `ConversationBufferMemory` with `ConversationBufferWindowMemory(k=2)`.  
This only remembers the last 2 exchanges.  
How does the agent's behaviour change?
```python
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True)
```

---

## Key Concepts Summary

| Concept | What it means |
|---------|--------------|
| Stateless LLM | Forgets everything after each call (Stage 1) |
| Short-term memory | Remembers within one session, lost on restart |
| `ConversationBufferMemory` | Stores ALL messages in a list |
| `PromptTemplate` | Reusable prompt with fill-in variables |
| `ConversationChain` | Glue that connects LLM + memory + prompt |
| `chain.predict()` | Send message, get reply, auto-save to memory |

---

## What's Next?

In **Stage 3** we add **tools** — the agent can now not only remember, but also *act*.  
It will detect the user's intent (debug vs explain vs review) and route to the right skill.

➡️ Move to [`../stage3_tool_agent/`](../stage3_tool_agent/README.md)
