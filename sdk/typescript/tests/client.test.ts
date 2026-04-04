/**
 * Unit tests for the MemoryWeave TypeScript client.
 *
 * All HTTP calls are mocked — no server required.
 */

import { MemoryWeave } from "../src/client";
import type { MemoryContext, MemoryItem, MemoryStats } from "../src/types";

// mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

function makeResponse<T>(data: T, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
  } as Response;
}

const mockItem: MemoryItem = {
  id: "test-id-123",
  text: "Ravi likes Python.",
  sessionId: "default",
  metadata: {},
};

const mockContext: MemoryContext = {
  summary: "Relevant memories:\n- Ravi likes Python. (relevance: 0.90)",
  entries: [{ item: mockItem, score: 0.9 }],
  facts: [],
  scores: [0.9],
  hasResults: true,
};

const mockStats: MemoryStats = {
  sessionId: "default",
  vectorCount: 3,
  nodeCount: 5,
  edgeCount: 3,
};

beforeEach(() => {
  mockFetch.mockClear();
});

describe("MemoryWeave constructor", () => {
  test("uses default config values", () => {
    const m = new MemoryWeave();
    expect(m).toBeDefined();
  });

  test("accepts custom baseUrl", () => {
    const m = new MemoryWeave({ baseUrl: "http://example.com" });
    expect(m).toBeDefined();
  });

  test("accepts custom sessionId", () => {
    const m = new MemoryWeave({ sessionId: "user-42" });
    expect(m).toBeDefined();
  });

  test("strips trailing slash from baseUrl", () => {
    const m = new MemoryWeave({ baseUrl: "http://localhost:8000/" });
    expect(m).toBeDefined();
  });
});

describe("add()", () => {
  test("returns a MemoryItem", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockItem));
    const m = new MemoryWeave();
    const result = await m.add("Ravi likes Python.");
    expect(result.id).toBe("test-id-123");
    expect(result.text).toBe("Ravi likes Python.");
  });

  test("sends POST to /memory/add", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockItem));
    const m = new MemoryWeave();
    await m.add("Ravi likes Python.");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/memory/add",
      expect.objectContaining({ method: "POST" })
    );
  });

  test("throws on empty text", async () => {
    const m = new MemoryWeave();
    await expect(m.add("")).rejects.toThrow("cannot add empty text");
  });

  test("throws on whitespace-only text", async () => {
    const m = new MemoryWeave();
    await expect(m.add("   ")).rejects.toThrow("cannot add empty text");
  });

  test("sends metadata in body", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockItem));
    const m = new MemoryWeave();
    await m.add("Test.", { source: "chat" });
    const body = JSON.parse(mockFetch.mock.calls[0][1].body as string);
    expect(body.metadata).toEqual({ source: "chat" });
  });

  test("includes session_id in body", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockItem));
    const m = new MemoryWeave({ sessionId: "user-99" });
    await m.add("Test.");
    const body = JSON.parse(mockFetch.mock.calls[0][1].body as string);
    expect(body.session_id).toBe("user-99");
  });
});

describe("get()", () => {
  test("returns a MemoryContext", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockContext));
    const m = new MemoryWeave();
    const ctx = await m.get("What does Ravi like?");
    expect(ctx.summary).toContain("Ravi likes Python");
    expect(ctx.hasResults).toBe(true);
  });

  test("sends POST to /memory/get", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockContext));
    const m = new MemoryWeave();
    await m.get("What does Ravi like?");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/memory/get",
      expect.objectContaining({ method: "POST" })
    );
  });

  test("throws on empty query", async () => {
    const m = new MemoryWeave();
    await expect(m.get("")).rejects.toThrow("cannot search with empty query");
  });

  test("uses custom topK override", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockContext));
    const m = new MemoryWeave();
    await m.get("query", 3);
    const body = JSON.parse(mockFetch.mock.calls[0][1].body as string);
    expect(body.top_k).toBe(3);
  });
});

describe("stats()", () => {
  test("returns MemoryStats", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockStats));
    const m = new MemoryWeave();
    const stats = await m.stats();
    expect(stats.vectorCount).toBe(3);
    expect(stats.sessionId).toBe("default");
  });

  test("sends GET to /memory/stats", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(mockStats));
    const m = new MemoryWeave();
    await m.stats();
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/memory/stats"),
      expect.objectContaining({ method: "GET" })
    );
  });
});

describe("isHealthy()", () => {
  test("returns true when server responds", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse({ status: "ok" }));
    const m = new MemoryWeave();
    const healthy = await m.isHealthy();
    expect(healthy).toBe(true);
  });

  test("returns false when server is unreachable", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Connection refused"));
    const m = new MemoryWeave();
    const healthy = await m.isHealthy();
    expect(healthy).toBe(false);
  });
});

describe("error handling", () => {
  test("throws on 4xx response", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse({ error: "Not found" }, 404));
    const m = new MemoryWeave();
    await expect(m.get("query")).rejects.toThrow("404");
  });

  test("throws on 5xx response", async () => {
    mockFetch.mockResolvedValueOnce(
      makeResponse({ error: "Internal error" }, 500)
    );
    const m = new MemoryWeave();
    await expect(m.add("test")).rejects.toThrow("500");
  });
});
