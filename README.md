# Research Digest Agent

A full-stack research assistant that takes a scientific question, autonomously searches Arxiv, and streams a structured digest back to the browser in real time.

---

## Prerequisites

- Python 3.11+
- Node 18+
- A running LiteLLM proxy (see `.env.example`)

---

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values:
   ```
   cp .env.example .env
   ```
3. Edit `.env` with your `LITELLM_BASE_URL`, `LITELLM_API_KEY`, and `LLM_MODEL`

---

## Running the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend automatically.

---

## Pass 2 — MCP integration

Pass 2 replaces the direct PubMed HTTP integration with the `mcp-pubmed` MCP server. Only `backend/main.py` changes. See the comment block in `backend/main.py` and the full loader implementation in `backend/agent/mcp_tools.py` for instructions.
