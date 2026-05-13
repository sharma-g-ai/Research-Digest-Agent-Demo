"""MCP tool loader for Pass 2 of the Research Digest Agent.

This file is only used in Pass 2. It replaces the direct pubmed_tools.py
integration by loading equivalent tools from the mcp-simple-pubmed MCP server via
langchain-mcp-adapters. graph.py and prompts.py do not change between passes —
only the tool source changes.

To activate Pass 2, update main.py to call load_mcp_tools() at startup instead
of importing from pubmed_tools.py. See the comment block in main.py for the
exact substitution.
"""

from langchain_mcp_adapters.client import MultiServerMCPClient


async def load_mcp_tools() -> tuple[list, object]:
    """Load LangChain-compatible tools from the PubMed MCP server.

    Creates a MultiServerMCPClient configured to launch mcp-simple-pubmed as a
    stdio subprocess, then retrieves the tools it exposes. The tools are
    returned as standard LangChain BaseTool instances and are passed directly
    to build_agent() — the agent graph is unaware of the MCP layer.

    IMPORTANT: The returned client object manages the lifetime of the MCP
    subprocess. It must be kept alive for the entire application lifetime.
    Assign it to a module-level variable in main.py (e.g. _mcp_client) to
    prevent garbage collection from killing the subprocess.

    Returns:
        A tuple of (tools, client) where:
            tools  — list of LangChain BaseTool instances from the MCP server
            client — the MultiServerMCPClient instance (must stay alive)
    """
    client = MultiServerMCPClient(
        {
            "pubmed": {
                "transport": "stdio",
                "command": "mcp-simple-pubmed",
            }
        }
    )
    tools = await client.get_tools()
    return tools, client
