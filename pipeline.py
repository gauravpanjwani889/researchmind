"""Runs the 4-step pipeline: search -> read -> write -> critique.

USE_AGENTS = False (default): search and read are plain code (fast: 2 model calls total).
USE_AGENTS = True: search and read are LLM agents that choose their own tool calls (slower).
"""
import re
from concurrent.futures import ThreadPoolExecutor

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain
from tools import scrape_text, search_text

USE_AGENTS = False
PAGES_TO_READ = 3


def run_search(topic: str) -> str:
    if USE_AGENTS:
        agent = build_search_agent()
        result = agent.invoke(
            {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
        )
        return result["messages"][-1].content
    return search_text(topic, max_results=5)


def run_reader(topic: str, search_results: str) -> str:
    if USE_AGENTS:
        agent = build_reader_agent()
        result = agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{search_results[:2000]}",
                    )
                ]
            }
        )
        return result["messages"][-1].content

    urls = re.findall(r"URL: (\S+)", search_results)[:PAGES_TO_READ]
    with ThreadPoolExecutor(max_workers=PAGES_TO_READ) as pool:  # scrape in parallel
        pages = list(pool.map(scrape_text, urls))
    return "\n\n".join(f"SOURCE: {u}\n{p}" for u, p in zip(urls, pages))


def run_writer(topic: str, search_results: str, scraped: str) -> str:
    research = (
        f"SEARCH RESULTS:\n{search_results}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{scraped}"
    )
    return writer_chain.invoke({"topic": topic, "research": research})


def run_critic(report: str) -> str:
    return critic_chain.invoke({"report": report})


def run_research_pipeline(topic: str) -> dict:
    state = {}
    print("Step 1 - Searching ...")
    state["search"] = run_search(topic)
    print("Step 2 - Reading pages ...")
    state["reader"] = run_reader(topic, state["search"])
    print("Step 3 - Writer drafting report ...")
    state["writer"] = run_writer(topic, state["search"], state["reader"])
    print("Step 4 - Critic reviewing ...")
    state["critic"] = run_critic(state["writer"])
    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    out = run_research_pipeline(topic)
    print("\n=== REPORT ===\n", out["writer"])
    print("\n=== CRITIC ===\n", out["critic"])
