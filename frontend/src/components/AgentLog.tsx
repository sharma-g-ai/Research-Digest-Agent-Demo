import { AgentEvent } from "../types";

export interface AgentLogProps {
  events: AgentEvent[];
}

// Renders only tool_call and tool_result events — thinking events are shown in DigestPanel.
export function AgentLog({ events }: AgentLogProps): JSX.Element | null {
  const visible = events.filter(
    (e) => e.type === "tool_call" || e.type === "tool_result"
  );

  if (visible.length === 0) return null;

  return (
    <div
      style={{
        background: "#f8f9fa",
        border: "1px solid #dee2e6",
        borderRadius: "6px",
        padding: "12px 16px",
        fontFamily: "monospace",
        fontSize: "13px",
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: "8px", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.05em", color: "#6c757d" }}>
        Agent Activity
      </div>
      {visible.map((event, index) => {
        if (event.type === "tool_call") {
          const query = event.input.query as string | undefined;
          return (
            <div key={index} style={{ marginBottom: "4px" }}>
              🔧 Called {event.name}{query ? ` — "${query}"` : ""}
            </div>
          );
        }
        if (event.type === "tool_result") {
          return (
            <div key={index} style={{ marginBottom: "4px" }}>
              ✅ {event.name}: {event.summary}
            </div>
          );
        }
        return null;
      })}
    </div>
  );
}
