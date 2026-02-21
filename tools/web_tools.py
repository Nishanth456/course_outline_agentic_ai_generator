"""LangChain tools for agents (PHASE 4+)."""


class PDFLoaderTool:
    """Load and parse uploaded PDF (PHASE 1)."""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        raise NotImplementedError("PHASE 1")


class WebSearchTool:
    """
    LangChain tool wrappers for web search (PHASE 4).
    
    Supports:
    - Tavily Search (primary)
    - DuckDuckGo (fallback)
    - SerpAPI (fallback)
    """
    
    @staticmethod
    def tavily_search(query: str, max_results: int = 10) -> list:
        """Search using Tavily."""
        raise NotImplementedError("PHASE 4")
    
    @staticmethod
    def duckduckgo_search(query: str, max_results: int = 10) -> list:
        """Search using DuckDuckGo."""
        raise NotImplementedError("PHASE 4")
    
    @staticmethod
    def serpapi_search(query: str, max_results: int = 10) -> list:
        """Search using SerpAPI."""
        raise NotImplementedError("PHASE 4")
