"""MemoryWeave — Universal long-term memory for any LLM application.

Gives any AI application persistent, searchable memory across sessions,
users, and models. Plug in with 3 lines of code.

    >>> import memoryweave
    >>> memory = memoryweave.MemoryWeave()
    >>> memory.add("My name is Ravi and I prefer Python.")
    >>> ctx = memory.get("What language does the user prefer?")

Author: Ravi Kashyap
GitHub: https://github.com/ravii-k/memoryweave
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

# [Ravi Kashyap] 2026-03-23 - Single source of truth for the version number.
# Bump this in pyproject.toml AND here on every release.
__version__ = "0.0.1"
__author__ = "Ravi Kashyap"
__license__ = "MIT"

# [Ravi Kashyap] 2026-03-23 - Public API surface.
# Only import what users should access directly via `memoryweave.X`.
# Internal modules should never be imported from here.
# Phase 4 will populate these imports once the classes are implemented.
from memoryweave.config import MemoryConfig  # noqa: F401

# TODO [Ravi Kashyap] 2026-03-23 - Uncomment as each phase completes.
# Tracked: will be enabled in Phase 4, Chapter 4.1
# from memoryweave.client import MemoryWeave      # noqa: F401

__all__ = [
    "__version__",
    "MemoryConfig",
    # "MemoryWeave",    # Phase 4
]
