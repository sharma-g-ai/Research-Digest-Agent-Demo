import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface DigestPanelProps {
  digest: string;
  isStreaming: boolean;
}

// Renders both the partial streaming digest (while running) and the final
// complete digest. Uses react-markdown with remark-gfm for full markdown
// support including tables, which are used in the Sources section.
export function DigestPanel({ digest, isStreaming }: DigestPanelProps): JSX.Element | null {
  if (digest === "") return null;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "10px", marginBottom: "8px" }}>
        <h2 style={{ margin: 0 }}>Research Digest</h2>
        {isStreaming && (
          <span style={{ fontSize: "12px", color: "#6c757d" }}>generating…</span>
        )}
      </div>
      <div
        style={{
          background: "#ffffff",
          border: "1px solid #dee2e6",
          borderRadius: "6px",
          padding: "20px 24px",
        }}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{digest}</ReactMarkdown>
      </div>
    </div>
  );
}
