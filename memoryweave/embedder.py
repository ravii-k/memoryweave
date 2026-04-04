"""Vector embedding — converts text into dense semantic vectors.

Uses sentence-transformers to produce dense vector representations
of text. Runs fully offline with no API key required.

all-MiniLM-L6-v2 is the default. It's ~80MB, fast on CPU, and accurate
enough for memory retrieval. Users who need better quality can swap to
a larger model in MemoryConfig.

The model is downloaded automatically on first use from HuggingFace Hub
and cached locally — subsequent loads are instant.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

from memoryweave.config import MemoryConfig
from memoryweave.errors import StoreError
from memoryweave.logger import get_logger

logger = get_logger(__name__)


class Embedder:
    """Converts text into dense semantic vectors using sentence-transformers.

    Runs locally — no API calls, no rate limits, no cost per embedding.
    The model is loaded once on init so repeated embed() calls are fast.

    Args:
    ----
        config: Controls which sentence-transformers model to use.

    Example:
    -------
        >>> embedder = Embedder(MemoryConfig())
        >>> vec = embedder.embed("Ravi prefers Python.")
        >>> len(vec)
        384

    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        self._model = self._load_model(config.embedding_model)

    def _load_model(self, model_name: str) -> SentenceTransformer:
        """Load the sentence-transformers model.

        Downloads from HuggingFace on first run, cached locally after.
        Raises StoreError if the model name is invalid or network fails.
        """
        try:
            logger.debug("loading embedding model %r", model_name)
            model = SentenceTransformer(model_name)
            dim = model.get_sentence_embedding_dimension()
            logger.debug("loaded %r — embedding dim: %d", model_name, dim)
            return model
        except Exception as e:
            raise StoreError(
                f"failed to load embedding model {model_name!r}: {e}. "
                "Check the model name or your internet connection on first run."
            ) from e

    @property
    def dimension(self) -> int:
        """Return the embedding dimension for the loaded model.

        all-MiniLM-L6-v2 → 384
        all-mpnet-base-v2 → 768
        """
        dim = self._model.get_sentence_embedding_dimension()
        if dim is None:
            return 0
        return int(dim)

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a dense vector.

        Args:
        ----
            text: Text to embed. Should be meaningful natural language —
                very short or empty strings produce noisy embeddings.

        Returns:
        -------
            Dense float vector. Length matches self.dimension (384 for
            the default all-MiniLM-L6-v2 model).

        Raises:
        ------
            StoreError: If embedding fails for any reason.

        """
        if not text or not text.strip():
            raise StoreError("cannot embed empty text")

        try:
            logger.debug("embedding %d chars", len(text))
            vec = self._model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        except Exception as e:
            raise StoreError(f"embedding failed: {e}") from e

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts in one batch pass.

        Much faster than calling embed() in a loop — sentence-transformers
        handles batching internally and parallelises across CPU cores.

        Args:
        ----
            texts: List of strings to embed. Empty list returns [].

        Returns:
        -------
            List of dense float vectors, one per input text, same order.

        Raises:
        ------
            StoreError: If any text is empty or embedding fails.

        """
        if not texts:
            return []

        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise StoreError(f"cannot embed empty text at index {i}")

        try:
            logger.debug("batch embedding %d texts", len(texts))
            vecs = self._model.encode(texts, convert_to_numpy=True)
            return [v.tolist() for v in vecs]
        except Exception as e:
            raise StoreError(f"batch embedding failed: {e}") from e

    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors.

        Returns a value between -1.0 and 1.0. Higher means more similar.
        Two identical texts will give ~1.0. Completely unrelated texts
        will give a value close to 0.0 or slightly negative.

        Args:
        ----
            vec_a: First embedding vector.
            vec_b: Second embedding vector.

        Returns:
        -------
            Cosine similarity score between -1.0 and 1.0.

        """
        if len(vec_a) != len(vec_b):
            raise StoreError(f"vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}")

        # manual cosine similarity — avoids numpy dependency in this method
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot / (norm_a * norm_b)
