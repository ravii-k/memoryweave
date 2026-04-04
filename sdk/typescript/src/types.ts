/**
 * Core types for the MemoryWeave TypeScript SDK.
 *
 * Phase 5, Chapter 5.1 — Ravi Kashyap 2026-04-04
 */

/** Configuration for the MemoryWeave client. */
export interface MemoryWeaveConfig {
  /** Base URL of the MemoryWeave REST API server. Default: http://localhost:8000 */
  baseUrl?: string;
  /** Session ID for memory isolation. Default: "default" */
  sessionId?: string;
  /** Max memories to retrieve per get() call. Default: 5 */
  topK?: number;
  /** Request timeout in milliseconds. Default: 30000 */
  timeout?: number;
  /** Optional API key for authenticated deployments. */
  apiKey?: string;
}

/** A single stored memory item. */
export interface MemoryItem {
  /** Unique ID for this memory. */
  id: string;
  /** The original text that was stored. */
  text: string;
  /** Session this memory belongs to. */
  sessionId: string;
  /** Optional metadata attached at add() time. */
  metadata: Record<string, unknown>;
}

/** Result returned by get() — ready to inject into an LLM prompt. */
export interface MemoryContext {
  /** Plain-text summary of relevant memories. Inject into system prompt. */
  summary: string;
  /** Matched memory items from vector search. */
  entries: Array<{ item: MemoryItem; score: number }>;
  /** Matched facts from the knowledge graph. */
  facts: Array<{ text: string; score: number }>;
  /** Relevance scores for entries. */
  scores: number[];
  /** True if there is any context to inject. */
  hasResults: boolean;
}

/** Stats for a session. */
export interface MemoryStats {
  sessionId: string;
  vectorCount: number;
  nodeCount: number;
  edgeCount: number;
}

/** Raw API response from the server. */
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}
