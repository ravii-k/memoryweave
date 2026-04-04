/**
 * MemoryWeave TypeScript SDK — public exports.
 *
 * @example
 * ```typescript
 * import { MemoryWeave } from "@memoryweave/sdk";
 *
 * const memory = new MemoryWeave({ sessionId: "user-123" });
 * await memory.add("My name is Ravi and I prefer Python.");
 * const ctx = await memory.get("What language does the user prefer?");
 * console.log(ctx.summary);
 * ```
 */

export { MemoryWeave } from "./client";
export type {
  MemoryContext,
  MemoryItem,
  MemoryStats,
  MemoryWeaveConfig,
} from "./types";
