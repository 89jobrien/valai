from typing import Optional

from duckduckgo_search import DDGS
from loguru import logger
from pydantic import BaseModel, Field
from tavily import TavilyClient

from valai.config import get_settings


class WebSearchArgs(BaseModel):
    """Input model for the web_search tool."""

    query: str = Field(..., description="The search query.")


def _tavily_search(query: str) -> Optional[str]:
    """Performs a search using the Tavily API."""
    logger.info(f"Attempting search with Tavily for query: '{query}'")
    settings = get_settings()
    if not settings.tavily_api_key:
        logger.warning("Tavily API key is not configured.")
        return None
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query=query, max_results=5)
        return str(response.get("results", "No results found."))
    except Exception as e:
        logger.error(f"Error searching Tavily: {e}")
        return None


def _ddg_search(query: str) -> str:
    """Performs a search using the DuckDuckGo API."""
    logger.info(f"Attempting search with DuckDuckGo for query: '{query}'")
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            return str(results) if results else "No results found."
    except Exception as e:
        logger.error(f"Error searching DuckDuckGo: {e}")
        return f"Error during DuckDuckGo search: {e}"


def web_search(args: WebSearchArgs) -> str:
    """Use this tool to search the web for up-to-date information.
    It first tries a high-quality search provider (Tavily) and falls back to a standard one (DuckDuckGo).
    """
    if not args.query:
        return "Error: Please provide a search query."

    # Try Tavily first
    tavily_result = _tavily_search(args.query)
    if tavily_result:
        return tavily_result

    # Fallback to DuckDuckGo
    logger.warning(
        "Tavily search failed or was unavailable. Falling back to DuckDuckGo."
    )
    return _ddg_search(args.query)
