"""Tests for the MemoryWeave client.

Phase 1 tests are limited to init behaviour and checking that the stub
methods raise NotImplementedError correctly. Not much to test yet since
nothing is implemented — the real behaviour tests come in Phase 4.

Keeping these here so the test structure is in place and ready to expand.
"""

import pytest

from memoryweave.client import MemoryWeave
from memoryweave.config import MemoryConfig


class TestMemoryWeaveInit:
    """Basic init tests — make sure the client sets itself up correctly."""

    def test_default_init(self) -> None:
        """No config passed — should fall back to MemoryConfig defaults."""
        memory = MemoryWeave()
        assert memory.config is not None
        assert memory.config.store_type == "memory"

    def test_custom_config(self) -> None:
        """Config passed in — should use it, not the defaults."""
        config = MemoryConfig(top_k=10, store_type="chroma")
        memory = MemoryWeave(config=config)
        assert memory.config.top_k == 10
        assert memory.config.store_type == "chroma"

    def test_repr(self) -> None:
        """repr should be useful for debugging — show store type and top_k."""
        memory = MemoryWeave()
        result = repr(memory)
        assert "MemoryWeave" in result
        assert "memory" in result


class TestMemoryWeaveStubs:
    """Stub methods should raise NotImplementedError until they're built.

    These tests will be replaced with real behaviour tests in Phase 4.
    For now they just confirm the stubs are wired up and not silently
    returning None or doing something unexpected.
    """

    def test_add_raises_not_implemented(self) -> None:
        """add() is a Phase 4 thing — should be loud about it."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.add("Some text")

    def test_get_raises_not_implemented(self) -> None:
        """get() is a Phase 4 thing — should be loud about it."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.get("Some query")

    def test_forget_raises_not_implemented(self) -> None:
        """forget() is a Phase 6 thing — should be loud about it."""
        memory = MemoryWeave()
        with pytest.raises(NotImplementedError):
            memory.forget()
