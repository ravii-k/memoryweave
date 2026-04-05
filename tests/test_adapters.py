"""Tests for LLM adapters — OpenAI and Anthropic."""

from __future__ import annotations

import pytest

from memoryweave import MemoryConfig, MemoryWeave
from memoryweave.adapters.anthropic import AnthropicAdapter
from memoryweave.adapters.openai import OpenAIAdapter


@pytest.fixture(scope="module")
def memory() -> MemoryWeave:
    m = MemoryWeave(MemoryConfig(default_session_id="adapter-test"))
    m.add("My name is Ravi and I prefer Python.")
    m.add("I am building MemoryWeave, an open-source memory SDK.")
    m.add("I use FastAPI for REST APIs.")
    return m


class TestOpenAIAdapter:
    def test_init(self, memory: MemoryWeave) -> None:
        adapter = OpenAIAdapter(memory)
        assert adapter.memory is memory

    def test_inject_adds_system_message(self, memory: MemoryWeave) -> None:
        adapter = OpenAIAdapter(memory)
        messages = [{"role": "user", "content": "Hello"}]
        result = adapter.inject(messages, "User is called Ravi.")
        assert result[0]["role"] == "system"
        assert "Ravi" in result[0]["content"]

    def test_inject_appends_to_existing_system(self, memory: MemoryWeave) -> None:
        adapter = OpenAIAdapter(memory)
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
        result = adapter.inject(messages, "User likes Python.")
        assert result[0]["role"] == "system"
        assert "You are helpful." in result[0]["content"]
        assert "Python" in result[0]["content"]

    def test_prepare_injects_memory(self, memory: MemoryWeave) -> None:
        adapter = OpenAIAdapter(memory)
        messages = [{"role": "user", "content": "What language do I prefer?"}]
        result = adapter.prepare(messages)
        system = result[0]["content"]
        assert "Python" in system

    def test_prepare_no_user_message_returns_unchanged(self, memory: MemoryWeave) -> None:
        adapter = OpenAIAdapter(memory)
        messages = [{"role": "assistant", "content": "Hello!"}]
        result = adapter.prepare(messages)
        assert result == messages

    def test_remember_stores_user_messages(self, memory: MemoryWeave) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="remember-test"))
        adapter = OpenAIAdapter(m)
        before = m.stats()["vector_count"]
        adapter.remember(
            [
                {"role": "user", "content": "I love Rust too."},
                {"role": "assistant", "content": "Great choice!"},
            ]
        )
        assert m.stats()["vector_count"] == before + 1


class TestAnthropicAdapter:
    def test_init(self, memory: MemoryWeave) -> None:
        adapter = AnthropicAdapter(memory)
        assert adapter.memory is memory

    def test_prepare_returns_tuple(self, memory: MemoryWeave) -> None:
        adapter = AnthropicAdapter(memory)
        messages = [{"role": "user", "content": "What is my name?"}]
        system, msgs = adapter.prepare(messages)
        assert isinstance(system, str)
        assert isinstance(msgs, list)

    def test_prepare_injects_memory_into_system(self, memory: MemoryWeave) -> None:
        adapter = AnthropicAdapter(memory)
        messages = [{"role": "user", "content": "What language do I prefer?"}]
        system, _ = adapter.prepare(messages)
        assert "Python" in system

    def test_prepare_no_user_message(self, memory: MemoryWeave) -> None:
        adapter = AnthropicAdapter(memory)
        messages = [{"role": "assistant", "content": "Hello!"}]
        system, msgs = adapter.prepare(messages)
        assert system == adapter.system_prompt

    def test_prepare_content_blocks_format(self, memory: MemoryWeave) -> None:
        adapter = AnthropicAdapter(memory)
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "What language do I prefer?"}]}
        ]
        system, _ = adapter.prepare(messages)
        assert "Python" in system

    def test_remember_stores_user_messages(self, memory: MemoryWeave) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="anthro-remember"))
        adapter = AnthropicAdapter(m)
        before = m.stats()["vector_count"]
        adapter.remember(
            [
                {"role": "user", "content": "I work in Meerut, India."},
                {"role": "assistant", "content": "Nice!"},
            ]
        )
        assert m.stats()["vector_count"] == before + 1

    def test_remember_content_blocks(self, memory: MemoryWeave) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="blocks-remember"))
        adapter = AnthropicAdapter(m)
        before = m.stats()["vector_count"]
        adapter.remember(
            [{"role": "user", "content": [{"type": "text", "text": "I use MacBook Air M2."}]}]
        )
        assert m.stats()["vector_count"] == before + 1
