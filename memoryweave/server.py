"""FastAPI REST server — exposes the MemoryWeave API over HTTP.

This is what the TypeScript SDK (and any other client) talks to.
Start it with:
    uvicorn memoryweave.server:app --reload

Phase 6, Chapter 6.1 — Ravi Kashyap 2026-04-04
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from memoryweave.client import MemoryWeave
from memoryweave.config import MemoryConfig
from memoryweave.logger import get_logger

logger = get_logger(__name__)

_API_KEY = os.environ.get("MEMORYWEAVE_API_KEY", "")
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def _verify_key(key: str | None = Security(_api_key_header)) -> None:
    """Verify API key if MEMORYWEAVE_API_KEY is set in environment.

    If the env var is not set the server runs unauthenticated (dev mode).
    """
    if _API_KEY and key != _API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


app = FastAPI(
    title="MemoryWeave API",
    description="Universal long-term memory for any LLM application.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# allow all origins in dev — tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# one MemoryWeave instance per session — stored in a dict
# in production this would be backed by Redis or a DB
_sessions: dict[str, MemoryWeave] = {}
_MAX_SESSIONS = 500  # prevent unbounded memory growth


def _get_client(session_id: str) -> MemoryWeave:
    """Get or create a MemoryWeave client for a session."""
    if session_id not in _sessions:
        if len(_sessions) >= _MAX_SESSIONS:
            oldest = next(iter(_sessions))
            del _sessions[oldest]
            logger.warning("session limit reached — evicted oldest session %r", oldest)
        _sessions[session_id] = MemoryWeave(MemoryConfig(default_session_id=session_id))
        logger.debug("created new session client for %r", session_id)
    return _sessions[session_id]


# ── Request / Response models ────────────────────────────────────────────────


class AddRequest(BaseModel):
    """Request body for POST /memory/add."""

    text: str
    session_id: str = "default"
    metadata: dict[str, Any] = {}


class GetRequest(BaseModel):
    """Request body for POST /memory/get."""

    query: str
    session_id: str = "default"
    top_k: int = 5


class ForgetRequest(BaseModel):
    """Request body for DELETE /memory/forget."""

    session_id: str = "default"


class MemoryItemResponse(BaseModel):
    """Response from POST /memory/add."""

    id: str
    text: str
    session_id: str
    metadata: dict[str, Any]


class ContextEntryResponse(BaseModel):
    """A single entry in the MemoryContext response."""

    text: str
    score: float
    id: str
    session_id: str


class MemoryContextResponse(BaseModel):
    """Response from POST /memory/get."""

    summary: str
    entries: list[ContextEntryResponse]
    facts: list[dict[str, Any]]
    scores: list[float]
    has_results: bool


class StatsResponse(BaseModel):
    """Response from GET /memory/stats."""

    session_id: str
    vector_count: int
    node_count: int
    edge_count: int


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Health check — returns ok if the server is running."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/memory/add", response_model=MemoryItemResponse, tags=["memory"])
async def add_memory(req: AddRequest, _: None = Depends(_verify_key)) -> MemoryItemResponse:
    """Extract, embed, and store a memory from raw text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    if len(req.text) > 10_000:
        raise HTTPException(status_code=400, detail="text too long — max 10,000 characters")

    try:
        client = _get_client(req.session_id)
        item = await client.async_add(req.text, metadata=req.metadata)
        return MemoryItemResponse(
            id=item.id,
            text=item.text,
            session_id=item.session_id,
            metadata=item.metadata,
        )
    except Exception as e:
        logger.error("add_memory failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/memory/get", response_model=MemoryContextResponse, tags=["memory"])
async def get_memory(req: GetRequest, _: None = Depends(_verify_key)) -> MemoryContextResponse:
    """Retrieve the most relevant memories for a query."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")

    try:
        client = _get_client(req.session_id)
        ctx = await client.async_get(req.query, top_k=req.top_k)

        entries = [
            ContextEntryResponse(
                text=item.text,
                score=score,
                id=item.id,
                session_id=item.session_id,
            )
            for item, score in ctx.entries
        ]
        facts = [{"text": text, "score": score} for text, score in ctx.facts]

        return MemoryContextResponse(
            summary=ctx.summary,
            entries=entries,
            facts=facts,
            scores=ctx.scores,
            has_results=ctx.has_results,
        )
    except Exception as e:
        logger.error("get_memory failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/memory/forget", tags=["memory"])
async def forget_memory(req: ForgetRequest, _: None = Depends(_verify_key)) -> dict[str, str]:
    """Wipe all memories for a session."""
    try:
        if req.session_id in _sessions:
            await _sessions[req.session_id].async_forget()
            del _sessions[req.session_id]
        return {"status": "ok", "session_id": req.session_id}
    except Exception as e:
        logger.error("forget_memory failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/memory/stats", response_model=StatsResponse, tags=["memory"])
async def get_stats(session_id: str = "default", _: None = Depends(_verify_key)) -> StatsResponse:
    """Get memory stats for a session."""
    try:
        client = _get_client(session_id)
        s = client.stats()
        return StatsResponse(
            session_id=s["session_id"],
            vector_count=s["vector_count"],
            node_count=s["node_count"],
            edge_count=s["edge_count"],
        )
    except Exception as e:
        logger.error("get_stats failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
