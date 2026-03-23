"""Tests for the MemoryWeave client.

Phase 1 tests only verify the client initialises correctly and that
stub methods raise NotImplementedError as expected. Full behaviour
tests will be added in Phase 4 when the methods are implemented.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

import pytest

from memoryweave.client import MemoryWeave
from memoryweave.config import MemoryConfig


class TestMemoryWeaveInit:
    """Tests that MemoryWeave initialises correctly.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def test_default_init(self) -> None:
        """Should initialise with default config when none is passed."""
        memory = MemoryWeave()
        assert memory.config is not None
        assert memory.config.store_type == "memory"

    def test_custom_config(self) -> None:
        """Should use the provided config when passed."""
        config = MemoryConfig(top_k=10, store_type="chroma")
        memory = MemoryWeave(config=config)
        assert memory.config.top_k == 10
        assert memory.config.store_type == "chroma"

    def test_repr(self) -> None:
        """Should return a useful string representation."""
        memory = MemoryWeave()
        result = repr(memory)
        assert "MemoryWeave" in result
        assert "memory" in result


class TestMemoryWeaveStubs:
    """Tests that stub methods raise NotImplementedError correctly.

    These tests will be replaced with real behaviour tests in Phase 4.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def test_add_raises_not_implemented(self) -> None:
        """memory.add() should raise NotImplementedError until Phase 4."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.add("Some text")

    def test_get_raises_not_implemented(self) -> None:
        """memory.get() should raise NotImplementedError until Phase 4."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.get("Some query")

    def test_forget_raises_not_implemented(self) -> None:
        """memory.forget() should raise NotImplementedError until Phase 6."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.forget()
