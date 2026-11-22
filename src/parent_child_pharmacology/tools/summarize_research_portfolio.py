"""Register the summarize_research_portfolio tool; domain behavior lives in services.literature."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.literature import summarize_research_portfolio


def register(mcp):
    return register_tool(mcp, summarize_research_portfolio, "literature")
