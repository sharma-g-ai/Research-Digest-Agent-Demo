// Discriminated union representing a single event emitted by the agent stream.
export type AgentEvent =
  | { type: "tool_call"; name: string; input: Record<string, unknown> }
  | { type: "tool_result"; name: string; summary: string }
  | { type: "thinking"; text: string }
  | { type: "done"; digest: string }
  | { type: "error"; message: string };

// Discriminated union representing the overall application state.
// Derive all display logic from this type — no separate boolean flags.
export type AppState =
  | { status: "idle" }
  | { status: "running"; events: AgentEvent[]; partialDigest: string }
  | { status: "done"; events: AgentEvent[]; digest: string }
  | { status: "error"; message: string };
