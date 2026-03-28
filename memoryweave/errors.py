"""Custom exceptions for MemoryWeave.

Keeping all errors in one place so users can catch them cleanly.
Everything inherits from MemoryWeaveError so you can do a broad
catch or a specific one depending on what you need.
"""


class MemoryWeaveError(Exception):
    """Base class for all MemoryWeave errors.

    Catch this if you want to handle any SDK error in one place.
    Catch the specific subclasses if you need finer control.
    """


class ConfigurationError(MemoryWeaveError):
    """Something is wrong with the MemoryConfig.

    Usually means an unsupported store_type, bad weight values,
    or a missing required field for the selected adapter.
    """


class ExtractionError(MemoryWeaveError):
    """The NLP pipeline couldn't process the input text.

    Most likely causes: spaCy model not installed, empty string
    passed to memory.add(), or the model returned garbage output.
    Will be raised from extractor.py once Phase 2 is built.
    """


class StoreError(MemoryWeaveError):
    """A vector store operation failed.

    Could be a ChromaDB connection issue, Qdrant timeout, or
    trying to write to a store that wasn't initialised properly.
    Will be raised from store.py once Phase 3 is built.
    """


class GraphError(MemoryWeaveError):
    """Something went wrong with the knowledge graph.

    Usually a malformed query or a corrupted graph state.
    Will be raised from graph.py once Phase 3 is built.
    """


class AdapterError(MemoryWeaveError):
    """An LLM adapter call failed.

    Most likely an invalid API key, rate limit hit, or network
    timeout talking to OpenAI / Anthropic / Ollama.
    Will be raised from adapters/ once Phase 4 is built.
    """


class SessionError(MemoryWeaveError):
    """A session operation failed.

    Raised when trying to access or delete a session that doesn't
    exist. Multi-user sessions come in Phase 6.
    """
