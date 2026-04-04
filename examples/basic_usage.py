"""Basic MemoryWeave usage — add and retrieve memories.

Run with:
    python examples/basic_usage.py
"""

from memoryweave import MemoryConfig, MemoryWeave

# create a memory instance — in-memory store by default
memory = MemoryWeave(MemoryConfig(default_session_id="demo"))

print("=== MemoryWeave Basic Usage Demo ===\n")

# add some memories
print("Adding memories...")
memory.add("My name is Ravi Kashyap and I am a Python developer.")
memory.add("I work at a startup building AI tools in Meerut, India.")
memory.add("I prefer Python over JavaScript for backend development.")
memory.add("My favourite framework is FastAPI for building REST APIs.")
memory.add("I use VS Code with Vim keybindings for coding.")

stats = memory.stats()
print(
    f"Stored {stats['vector_count']} memories, "
    f"{stats['node_count']} graph nodes, "
    f"{stats['edge_count']} graph edges\n"
)

# retrieve memories
queries = [
    "What language does this person prefer?",
    "Where does Ravi work?",
    "What tools does the developer use?",
]

for query in queries:
    print(f"Query: {query}")
    ctx = memory.get(query)
    if ctx.has_results:
        print(f"Context:\n{ctx.summary}")
    else:
        print("No relevant memories found.")
    print()
