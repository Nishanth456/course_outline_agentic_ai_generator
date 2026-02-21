"""PHASE 4: Web Search Agent stub."""

from agents.base import WebSearchAgent


class PublicWebSearchAgent(WebSearchAgent):
    """
    Implementation for PHASE 4.
    
    Uses LangChain Tools + fallback logic:
    1. Try Tavily Search
    2. Fallback to DuckDuckGo
    3. Fallback to SerpAPI (if configured)
    """
    
    pass
