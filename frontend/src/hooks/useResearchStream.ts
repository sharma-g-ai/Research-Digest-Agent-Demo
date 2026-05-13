import { useCallback, useState } from "react";
import { AgentEvent, AppState } from "../types";

interface UseResearchStreamResult {
  state: AppState;
  run: (question: string) => Promise<void>;
  reset: () => void;
}

export function useResearchStream(): UseResearchStreamResult {
  const [state, setState] = useState<AppState>({ status: "idle" });

  const run = useCallback(async (question: string): Promise<void> => {
    try {
      // 1. Set state to running
      setState({ status: "running", events: [], partialDigest: "" });

      // 2. POST to /api/research with { question }
      const response = await fetch("/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      // 3. Get response.body as a ReadableStream
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // 4. Decode chunks, buffer incomplete SSE frames (split on \n\n)
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const frames = buffer.split("\n\n");
        buffer = frames.pop()!;

        for (const frame of frames) {
          // 5. Parse each complete frame: extract event name and data JSON
          const eventMatch = frame.match(/^event: (.+)$/m);
          const dataMatch = frame.match(/^data: (.+)$/m);
          if (!eventMatch || !dataMatch) continue;
          const eventName = eventMatch[1];
          let parsed: Record<string, unknown>;
          try {
            parsed = JSON.parse(dataMatch[1]);
          } catch {
            continue;
          }

          // 6. Dispatch to state based on event type
          const event = { type: eventName, ...parsed } as AgentEvent;
          setState((prev) => {
            if (prev.status !== "running") return prev;
            if (event.type === "tool_call" || event.type === "tool_result") {
              return { ...prev, events: [...prev.events, event] };
            }
            if (event.type === "thinking") {
              return { ...prev, partialDigest: prev.partialDigest + event.text };
            }
            if (event.type === "done") {
              return { status: "done", events: prev.events, digest: event.digest };
            }
            if (event.type === "error") {
              return { status: "error", message: event.message };
            }
            return prev;
          });
        }
      }
    } catch (error) {
      setState({ status: "error", message: (error as Error).message });
    }
  }, []);

  const reset = useCallback((): void => {
    setState({ status: "idle" });
  }, []);

  return { state, run, reset };
}
