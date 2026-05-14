"""LangGraph agent graph.

This file never changes between Pass 1 and Pass 2. It is tool-agnostic by
design: it receives a list of LangChain BaseTool instances and wires them into
a compiled ReAct agent. The caller (main.py) is responsible for supplying the
correct tools for each pass.
"""

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from config import get_llm
from agent.prompts import SYSTEM_PROMPT


def build_agent(tools: list[BaseTool], prompt: str = SYSTEM_PROMPT):
    """Build and return a compiled LangGraph ReAct agent.

    Accepts a list of LangChain BaseTool instances and returns a compiled
    LangGraph ReAct agent. Pass 1 and Pass 2 both call this function — only
    the tools argument differs. The agent is intended to be instantiated once
    at application startup and reused across requests.

    Args:
        tools: A list of LangChain BaseTool instances to make available to
            the agent. In Pass 1 these come from pubmed_tools.py; in Pass 2
            they come from the MCP server via mcp_tools.py.

    Returns:
        A compiled LangGraph CompiledGraph ready for streaming with
        astream_events.
    """
    llm = get_llm()

    agent = create_react_agent(llm, tools, prompt=prompt)

    return agent
