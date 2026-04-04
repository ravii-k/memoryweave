/**
 * MemoryWeave TypeScript client — wraps the REST API.
 *
 * Works with any MemoryWeave server (Python FastAPI backend).
 * All network calls use the native fetch API (Node 18+ / browsers).
 *
 * Phase 5, Chapter 5.2 — Ravi Kashyap 2026-04-04
 */

import type {
  MemoryContext,
  MemoryItem,
  MemoryStats,
  MemoryWeaveConfig,
} from "./types";

const DEFAULT_BASE_URL = "http://localhost:8000";
const DEFAULT_SESSION_ID = "default";
const DEFAULT_TOP_K = 5;
const DEFAULT_TIMEOUT = 30_000;

/**
 * MemoryWeave TypeScript client.
 *
 * Thin HTTP wrapper around the MemoryWeave REST API. Mirrors the
 * Python SDK's interface so switching between them is seamless.
 *
 * @example
 * ```typescript
 * const memory = new MemoryWeave({ sessionId: "user-123" });
 * await memory.add("My name is Ravi and I prefer Python.");
 * const ctx = await memory.get("What language does the user prefer?");
 * console.log(ctx.summary);
 * ```
 */
export class MemoryWeave {
  private readonly baseUrl: string;
  private readonly sessionId: string;
  private readonly topK: number;
  private readonly timeout: number;
  private readonly headers: Record<string, string>;

  constructor(config: MemoryWeaveConfig = {}) {
    this.baseUrl = (config.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.sessionId = config.sessionId ?? DEFAULT_SESSION_ID;
    this.topK = config.topK ?? DEFAULT_TOP_K;
    this.timeout = config.timeout ?? DEFAULT_TIMEOUT;

    this.headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    if (config.apiKey) {
      this.headers["Authorization"] = `Bearer ${config.apiKey}`;
    }
  }

  /**
   * Add a memory from raw text.
   *
   * Sends the text to the server which runs the full pipeline:
   * NLP extraction → embedding → vector store → knowledge graph.
   *
   * @param text - Raw text to remember.
   * @param metadata - Optional key-value metadata to attach.
   * @returns The stored MemoryItem.
   */
  async add(
    text: string,
    metadata: Record<string, unknown> = {}
  ): Promise<MemoryItem> {
    if (!text || !text.trim()) {
      throw new Error("cannot add empty text to memory");
    }

    const response = await this.request<MemoryItem>("/memory/add", {
      method: "POST",
      body: JSON.stringify({
        text,
        metadata,
        session_id: this.sessionId,
      }),
    });

    return response;
  }

  /**
   * Retrieve the most relevant memories for a query.
   *
   * @param query - Natural language query (usually the user's latest message).
   * @param topK - Override the default top_k for this call.
   * @returns MemoryContext with summary, entries, facts, and scores.
   */
  async get(query: string, topK?: number): Promise<MemoryContext> {
    if (!query || !query.trim()) {
      throw new Error("cannot search with empty query");
    }

    const k = topK ?? this.topK;

    const response = await this.request<MemoryContext>("/memory/get", {
      method: "POST",
      body: JSON.stringify({
        query,
        top_k: k,
        session_id: this.sessionId,
      }),
    });

    return response;
  }

  /**
   * Wipe all memories for the current session.
   */
  async forget(sessionId?: string): Promise<void> {
    const sid = sessionId ?? this.sessionId;

    await this.request<void>("/memory/forget", {
      method: "DELETE",
      body: JSON.stringify({ session_id: sid }),
    });
  }

  /**
   * Get memory stats for the current session.
   */
  async stats(sessionId?: string): Promise<MemoryStats> {
    const sid = sessionId ?? this.sessionId;
    return this.request<MemoryStats>(`/memory/stats?session_id=${sid}`, {
      method: "GET",
    });
  }

  /**
   * Check if the server is reachable.
   *
   * @returns true if the server responds to the health endpoint.
   */
  async isHealthy(): Promise<boolean> {
    try {
      await this.request<{ status: string }>("/health", { method: "GET" });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Make an authenticated HTTP request to the API.
   */
  private async request<T>(
    path: string,
    options: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: this.headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => "unknown error");
        throw new Error(
          `MemoryWeave API error ${response.status}: ${errorText}`
        );
      }

      // DELETE responses may have no body
      if (response.status === 204) {
        return undefined as T;
      }

      const data = (await response.json()) as T;
      return data;
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error(
          `MemoryWeave request timed out after ${this.timeout}ms`
        );
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }
}
