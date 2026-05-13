import { useState } from "react";

export interface SearchFormProps {
  onSubmit: (question: string) => void;
  disabled: boolean;
}

export function SearchForm({ onSubmit, disabled }: SearchFormProps): JSX.Element {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px" }}>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="e.g. What are recent findings on GLP-1 agonists for obesity?"
        disabled={disabled}
        style={{ flex: 1, padding: "8px 12px", fontSize: "14px" }}
      />
      <button
        type="submit"
        disabled={disabled || value.trim() === ""}
        style={{ padding: "8px 16px", fontSize: "14px", cursor: disabled ? "not-allowed" : "pointer" }}
      >
        {disabled ? "Searching…" : "Research"}
      </button>
    </form>
  );
}
