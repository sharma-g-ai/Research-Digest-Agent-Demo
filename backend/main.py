import asyncio
import contextlib
import json
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.graph import build_agent
from agent.mcp_tools import load_mcp_tools
from agent.prompts import ARXIV_SYSTEM_PROMPT

load_dotenv()

# Module-level references populated during lifespan startup.
_mcp_client = None
agent = None


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global agent, _mcp_client
    tools, _mcp_client = await load_mcp_tools()
    agent = build_agent(tools, prompt=ARXIV_SYSTEM_PROMPT)
    yield


app = FastAPI(title="Research Digest Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str


# Active: arXiv via MCP (Pass 2)
# To roll back to direct arXiv tools (Pass 1):
#   from agent.arxiv_tools import search_arxiv, fetch_paper
#   remove the lifespan above and replace with module-level:
#   tools = [search_arxiv, fetch_paper]
#   agent = build_agent(tools, prompt=ARXIV_SYSTEM_PROMPT)


async def stream_agent(question: str) -> AsyncGenerator[str, None]:
    """Run the agent and yield SSE-formatted events as the agent progresses.

    Streams four event types to the client:

        tool_call   — emitted when the agent invokes a tool.
                      Payload: {"name": str, "input": dict}

        tool_result — emitted when a tool returns. Contains a human-readable
                      summary, not the raw output.
                      Payload: {"name": str, "summary": str}

        thinking    — emitted for each token the LLM streams while composing
                      the final digest.
                      Payload: {"text": str}

        done        — emitted once when the agent finishes. Contains the
                      complete digest text.
                      Payload: {"digest": str}

    All events follow the SSE wire format:
        event: {name}\\ndata: {json}\\n\\n

    Args:
        question: The research question submitted by the user.

    Yields:
        SSE-formatted strings, one per event.
    """
    async for event in agent.astream_events(
        {"messages": [("human", question)]}, version="v2"
    ):
        try:
            event_type = event["event"]

            if event_type == "on_tool_start":
                payload = {"name": event["name"], "input": event["data"].get("input", {})}
                yield f"event: tool_call\ndata: {json.dumps(payload)}\n\n"

            elif event_type == "on_tool_end":
                output = event["data"].get("output", "")
                if isinstance(output, list):
                    summary = f"{len(output)} article(s) retrieved"
                elif isinstance(output, dict) and "title" in output:
                    summary = output["title"]
                else:
                    summary = str(output)[:120]
                payload = {"name": event["name"], "summary": summary}
                yield f"event: tool_result\ndata: {json.dumps(payload)}\n\n"

            elif event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    payload = {"text": chunk.content}
                    yield f"event: thinking\ndata: {json.dumps(payload)}\n\n"

            elif event_type == "on_chain_end" and event["name"] == "LangGraph":
                last_message = event["data"]["output"]["messages"][-1]
                payload = {"digest": last_message.content}
                yield f"event: done\ndata: {json.dumps(payload)}\n\n"

        except Exception as e:
            payload = {"message": str(e)}
            yield f"event: error\ndata: {json.dumps(payload)}\n\n"


@app.post("/api/research")
async def research(req: ResearchRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_agent(req.question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
