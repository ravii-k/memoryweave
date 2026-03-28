"""Vector embedding — converts text into dense semantic vectors.

Using sentence-transformers here because it runs fully offline with no
API key needed. That's a hard requirement — users shouldn't have to pay
for embeddings just to get started.

all-MiniLM-L6-v2 is the default. It's 80MB, fast on CPU, and accurate
enough for memory retrieval. Users who need better quality can swap to
a larger model in MemoryConfig.
"""

from __future__ import annotations

# will be uncommented in Phase 3, Chapter 3.1
# from sentence_transformers import SentenceTransformer
from memoryweave.config import MemoryConfig


class Embedder:
    """Turns text into dense vectors using sentence-transformers.

    Runs locally — no API calls, no rate limits, no cost per embedding.
    The model gets loaded once on init so repeated calls are fast.

    Args:
        config: Controls which sentence-transformers model to load.
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        # loading model on init so we don't pay the startup cost
        # on every embed() call — can take 1-2s on first load
        # self._model = SentenceTransformer(config.embedding_model)

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a dense vector.

        Args:
            text: Text to embed. Should be a clean, meaningful string —
                very short or empty strings produce noisy embeddings.

        Returns:
            Dense float vector. all-MiniLM-L6-v2 produces 384 dimensions.
        """
        # Phase 3, Chapter 3.1
        raise NotImplementedError("coming in Phase 3, Chapter 3.1")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts in one batch pass.

        Much faster than calling embed() in a loop — sentence-transformers
        handles batching internally and parallelises across CPU cores.

        Args:
            texts: List of strings to embed.

        Returns:
            List of dense float vectors, one per input text, same order.
        """
        # Phase 3, Chapter 3.1 — batch support is critical for
        # performance when doing bulk memory ingestion
        raise NotImplementedError("coming in Phase 3, Chapter 3.1")
