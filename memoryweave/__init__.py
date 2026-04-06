"""MemoryWeave — Universal long-term memory for any LLM application.

Plug into any LLM app with 3 lines of code. Handles extraction,
storage, and retrieval automatically.

    >>> import memoryweave
    >>> memory = memoryweave.MemoryWeave()
    >>> memory.add("My name is Ravi and I prefer Python.")
    >>> ctx = memory.get("What language does the user prefer?")
    >>> print(ctx.summary)

Author: Ravi Kashyap
GitHub: https://github.com/ravii-k
Email: kashyap01212@gmail.com
Started: March 2026
"""

from memoryweave.client import MemoryWeave
from memoryweave.config import MemoryConfig
from memoryweave.logger import configure_logging
from memoryweave.ranker import MemoryContext

# keeping version in sync with pyproject.toml
__version__ = "1.1.0"
__author__ = "Ravi Kashyap"
__license__ = "MIT"

__all__ = [
    "__version__",
    "MemoryWeave",
    "MemoryConfig",
    "MemoryContext",
    "configure_logging",
]
