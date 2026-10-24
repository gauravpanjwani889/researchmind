"""Tools: web search (Tavily) and page scraping. Plain functions + LangChain tool wrappers."""
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from langchain.tools import tool
from tavily import TavilyClient

_cfg = dotenv_values(Path(__file__).parent / ".env")
_tavily = None


def _get_tavily() -> TavilyClient:
    """Create the Tavily client lazily so a missing key gives a clear error."""
    global _tavily
    if _tavily is None:
        key = _cfg.get("TAVILY_API_KEY") or os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("TAVILY_API_KEY is missing. Add it to your .env file.")
        _tavily = TavilyClient(api_key=key)
    return _tavily


# ---------- plain functions (used directly by the fast pipeline) ----------
def search_text(query: str, max_results: int = 5) -> str:
    """Search the web; return titles, URLs and snippets as text."""
    results = _get_tavily().search(query=query, max_results=max_results)["results"]
    out = [
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        for r in results
    ]
    return "\n----\n".join(out)


def scrape_text(url: str, limit: int = 2500) -> str:
    """Download a page and return its clean text (first `limit` characters)."""
    try:
        resp = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:limit]
    except Exception as e:
        return f"Could not scrape URL: {e}"


# ---------- LangChain tool wrappers (used only if USE_AGENTS = True) ----------
@tool
def web_search(query: str) -> str:
    """Search the web for recent, reliable information on a topic.
    Returns titles, URLs and snippets."""
    return search_text(query)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a URL for deeper reading."""
    return scrape_text(url)
