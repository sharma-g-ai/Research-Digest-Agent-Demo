import { useResearchStream } from "./hooks/useResearchStream";
import { AgentLog } from "./components/AgentLog";
import { DigestPanel } from "./components/DigestPanel";
import { SearchForm } from "./components/SearchForm";
import { AgentEvent } from "./types";

export default function App(): JSX.Element {
  const { state, run, reset } = useResearchStream();

  // TODO: derive from state
  const isRunning: boolean = state.status === "running";
  const events: AgentEvent[] =
    state.status === "running" || state.status === "done" ? state.events : [];
  const digest: string =
    state.status === "running"
      ? state.partialDigest
      : state.status === "done"
        ? state.digest
        : "";

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px" }}>
      <header style={{ marginBottom: "32px" }}>
        <h1 style={{ margin: "0 0 8px" }}>Research Digest Agent</h1>
        <p style={{ margin: 0, color: "#6c757d" }}>
          Ask a scientific question. The agent searches Arxiv and synthesises a structured digest in real time.
        </p>
      </header>

      <SearchForm onSubmit={run} disabled={isRunning} />

      {state.status === "error" && (
        <div style={{ marginTop: "16px", padding: "12px 16px", background: "#fff3f3", border: "1px solid #f5c2c7", borderRadius: "6px", color: "#842029" }}>
          <span>{state.message}</span>
          <button onClick={reset} style={{ marginLeft: "12px", cursor: "pointer" }}>Try again</button>
        </div>
      )}

      {events.length > 0 && (
        <div style={{ marginTop: "24px" }}>
          <AgentLog events={events} />
        </div>
      )}

      {digest && (
        <div style={{ marginTop: "24px" }}>
          <DigestPanel digest={digest} isStreaming={isRunning} />
        </div>
      )}

      {state.status === "done" && (
        <div style={{ marginTop: "16px" }}>
          <button onClick={reset} style={{ padding: "8px 16px", cursor: "pointer" }}>New Question</button>
        </div>
      )}
    </div>
  );
}
