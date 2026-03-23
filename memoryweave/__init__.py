"""MemoryWeave — Universal long-term memory for any LLM application.

Plug into any LLM app with 3 lines of code. Handles extraction,
storage, and retrieval automatically.

    >>> import memoryweave
    >>> memory = memoryweave.MemoryWeave()
    >>> memory.add("My name is Ravi and I prefer Python.")
    >>> ctx = memory.get("What language does the user prefer?")

Author: Ravi Kashyap
GitHub: https://github.com/ravii-k
Email: kashyap01212@gmail.com
Started: March 2026
"""

# keeping version in sync with pyproject.toml manually for now —
# might automate this with bump2version later
__version__ = "0.0.1"
__author__ = "Ravi Kashyap"
__license__ = "MIT"

# only exposing MemoryConfig here for now since the main client
# isn't ready yet — will uncomment MemoryWeave once Phase 4 is done
from memoryweave.config import MemoryConfig  # noqa: F401

# from memoryweave.client import MemoryWeave  # Phase 4

__all__ = [
    "__version__",
    "MemoryConfig",
    # "MemoryWeave",  # coming in Phase 4
]
