"""The four AI components: search agent, reader agent, writer chain, critic chain."""
from pathlib import Path

from dotenv import dotenv_values
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools import scrape_url, web_search
import os

# Read keys straight from .env so a stale system variable can't override them.
_cfg = dotenv_values(Path(__file__).parent / ".env")
api_key=_cfg.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),

# One shared model (Groq free tier). temperature=0 keeps output factual.
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=_cfg.get("GROQ_API_KEY"),
    max_retries=6,  # free tier is rate limited; retry on 429
)


# 1) Search agent: decides what to search and calls the web_search tool
def build_search_agent():
    return create_agent(model=llm, tools=[web_search])


# 2) Reader agent: picks the best URL and calls scrape_url for deeper content
def build_reader_agent():
    return create_agent(model=llm, tools=[scrape_url])


# 3) Writer chain: turns gathered research into a structured report
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional. Only use facts present in the research above.""",
        ),
    ]
)
writer_chain = writer_prompt | llm | StrOutputParser()


# 4) Critic chain: scores the report and suggests improvements
critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)
critic_chain = critic_prompt | llm | StrOutputParser()
