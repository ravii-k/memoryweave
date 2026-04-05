"""MemoryWeave v1.0.0 — Personal Demo
====================================
Run with:
    cd /Users/ravi/memoryweave
    source .venv/bin/activate
    python demo_usage.py
"""

from memoryweave import MemoryConfig, MemoryWeave

print("=" * 58)
print("  MemoryWeave v1.0.0 — Live Demo")
print("=" * 58)
print()

# ── 1. Create a memory instance ──────────────────────────────────
memory = MemoryWeave(MemoryConfig(default_session_id="ravi-demo"))

# ── 2. Feed it facts ─────────────────────────────────────────────
print("📝 Adding memories...\n")
facts = [
    "My name is Ravi Kashyap and I am a Python developer from Meerut, India.",
    "I prefer FastAPI for REST APIs and ChromaDB for vector storage.",
    "I use Python 3.14 on an M2 MacBook Air.",
    "I am building an open-source memory SDK called MemoryWeave.",
    "I am interested in intraday options trading on Nifty 50.",
    "I am also developing a macOS trading journal app called R-Journal in SwiftUI.",
]

for fact in facts:
    memory.add(fact)
    print(f"  ✅  {fact[:65]}{'...' if len(fact) > 65 else ''}")

print()

# ── 3. Stats ─────────────────────────────────────────────────────
stats = memory.stats()
print("📊 Memory stats:")
print(f"   Vectors stored  : {stats['vector_count']}")
print(f"   Graph nodes     : {stats['node_count']}")
print(f"   Graph edges     : {stats['edge_count']}")
print()

# ── 4. Query ─────────────────────────────────────────────────────
queries = [
    "What programming language does Ravi prefer?",
    "What projects is this person working on?",
    "What is their trading interest?",
    "What computer does the developer use?",
    "Where is this person from?",
]

print("🔍 Querying memory...\n")
for query in queries:
    ctx = memory.get(query)
    print(f"  Q: {query}")
    if ctx.has_results:
        lines = [l.strip() for l in ctx.summary.splitlines() if l.strip()]
        best = lines[1] if len(lines) > 1 else lines[0]
        print(f"  A: {best}")
    else:
        print("  A: No relevant memories found.")
    print()

# ── 5. Show LLM prompt injection ─────────────────────────────────
print("=" * 58)
print("  LLM Prompt Injection Example")
print("=" * 58)
print()

user_message = "What stack should I use for my next API project?"
ctx = memory.get(user_message)

system = "You are a helpful coding assistant."
if ctx.has_results:
    system += f"\n\nWhat you know about this user:\n{ctx.summary}"

print("SYSTEM PROMPT:")
print("-" * 40)
print(system)
print("-" * 40)
print(f"\nUSER: {user_message}")
print()
print("→ Send these to OpenAI / Anthropic / any LLM")
print()
print("=" * 58)
print("  Demo complete! github.com/ravii-k/memoryweave")
print("=" * 58)
