# tool.py
from langchain_core.tools import tool

@tool
def sample_tool(query: str) -> str:
    """Sample tool for the agent."""
    return f"Result for {query}"

# Define your LangGraph tools here
tools = [sample_tool]
