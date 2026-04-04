"""Tests for the FastAPI REST server.

Uses FastAPI's TestClient — no actual HTTP server needed.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from memoryweave.server import _sessions, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions() -> None:
    """Wipe all sessions before each test for isolation."""
    _sessions.clear()


class TestHealth:
    def test_health_returns_ok(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_returns_version(self) -> None:
        resp = client.get("/health")
        assert "version" in resp.json()


class TestAddMemory:
    def test_add_returns_200(self) -> None:
        resp = client.post(
            "/memory/add",
            json={"text": "Ravi likes Python.", "session_id": "test-add"},
        )
        assert resp.status_code == 200

    def test_add_returns_item(self) -> None:
        resp = client.post(
            "/memory/add",
            json={"text": "Ravi works at Google.", "session_id": "test-add2"},
        )
        data = resp.json()
        assert "id" in data
        assert data["text"] == "Ravi works at Google."

    def test_add_empty_text_returns_400(self) -> None:
        resp = client.post(
            "/memory/add",
            json={"text": "", "session_id": "test"},
        )
        assert resp.status_code == 400

    def test_add_with_metadata(self) -> None:
        resp = client.post(
            "/memory/add",
            json={
                "text": "Test memory.",
                "session_id": "test-meta",
                "metadata": {"source": "unit-test"},
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["source"] == "unit-test"


class TestGetMemory:
    def test_get_returns_200(self) -> None:
        # add something first
        client.post(
            "/memory/add",
            json={"text": "Ravi prefers Python.", "session_id": "get-test"},
        )
        resp = client.post(
            "/memory/get",
            json={"query": "Python", "session_id": "get-test"},
        )
        assert resp.status_code == 200

    def test_get_returns_context_shape(self) -> None:
        client.post(
            "/memory/add",
            json={"text": "Ravi likes Python.", "session_id": "shape-test"},
        )
        resp = client.post(
            "/memory/get",
            json={"query": "Python", "session_id": "shape-test"},
        )
        data = resp.json()
        assert "summary" in data
        assert "entries" in data
        assert "facts" in data
        assert "has_results" in data

    def test_get_empty_store_returns_empty_context(self) -> None:
        resp = client.post(
            "/memory/get",
            json={"query": "anything", "session_id": "empty-xyz"},
        )
        assert resp.status_code == 200
        assert resp.json()["has_results"] is False

    def test_get_empty_query_returns_400(self) -> None:
        resp = client.post(
            "/memory/get",
            json={"query": "", "session_id": "test"},
        )
        assert resp.status_code == 400

    def test_get_has_results_after_add(self) -> None:
        client.post(
            "/memory/add",
            json={"text": "Ravi loves Python.", "session_id": "result-test"},
        )
        resp = client.post(
            "/memory/get",
            json={"query": "Python", "session_id": "result-test"},
        )
        assert resp.json()["has_results"] is True


class TestForgetMemory:
    def test_forget_returns_ok(self) -> None:
        client.post(
            "/memory/add",
            json={"text": "Remember this.", "session_id": "forget-test"},
        )
        resp = client.request(
            "DELETE",
            "/memory/forget",
            json={"session_id": "forget-test"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_forget_clears_memories(self) -> None:
        client.post(
            "/memory/add",
            json={"text": "Remember this.", "session_id": "forget-clear"},
        )
        client.request(
            "DELETE",
            "/memory/forget",
            json={"session_id": "forget-clear"},
        )
        resp = client.post(
            "/memory/get",
            json={"query": "anything", "session_id": "forget-clear"},
        )
        assert resp.json()["has_results"] is False


class TestStats:
    def test_stats_returns_200(self) -> None:
        resp = client.get("/memory/stats?session_id=stats-test")
        assert resp.status_code == 200

    def test_stats_returns_correct_shape(self) -> None:
        resp = client.get("/memory/stats?session_id=shape-test")
        data = resp.json()
        assert "session_id" in data
        assert "vector_count" in data
        assert "node_count" in data
        assert "edge_count" in data

    def test_stats_increments_after_add(self) -> None:
        assert (
            client.get("/memory/stats?session_id=inc-test").json()["vector_count"] == 0
        )
        client.post(
            "/memory/add",
            json={"text": "Ravi likes Python.", "session_id": "inc-test"},
        )
        assert (
            client.get("/memory/stats?session_id=inc-test").json()["vector_count"] == 1
        )
