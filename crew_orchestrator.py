r"""
CrewAI Orchestrator
====================
Implements the pipeline shown in the architecture diagram:

  Input Processing Agent
          |
  Orchestrator (fan-out)
     /       |        \
Web Search  Market   Competitor
 Agent      Research   Agent
(Tavily)    Agent      (Chroma RAG)
(Tavily)
     \       |        /
  Trend Analysis Agent (fan-in & synthesize)
          |
  Validation & Scoring Agent
          |
  Report Generation Agent
          |
    Final structured JSON

CrewAI doesn't have a literal "Orchestrator" node -- the Crew object IS the
orchestrator. Fan-out is achieved by marking the three research tasks
async_execution=True (they run in parallel threads). Fan-in is achieved by
giving the Trend Analysis task `context=[...]` pointing at all three, so it
waits for all of them and receives their combined output.
"""

import os
import json
from importlib import import_module
from typing import List, Type

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from pydantic import BaseModel, Field

from search_optimization import build_search_queries


def load_dotenv(path: str | None = None) -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    if not os.path.isfile(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                os.environ.setdefault(key, value)

try:
    # Resolve CrewAI dynamically so editors do not report a missing optional
    # dependency at import-analysis time, while retaining normal runtime use.
    _crewai = import_module("crewai")
    Agent = _crewai.Agent
    Task = _crewai.Task
    Crew = _crewai.Crew
    Process = _crewai.Process
    BaseTool = import_module("crewai.tools").BaseTool
except ImportError as exc:
    raise RuntimeError(
        "CrewAI is required. Install it with `pip install crewai`."
    ) from exc

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TAVILY_API_KEY or not OPENROUTER_API_KEY:
    missing_keys = [
        name for name, value in {
            "TAVILY_API_KEY": TAVILY_API_KEY,
            "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
        }.items()
        if not value
    ]
    raise RuntimeError(
        f"Missing {', '.join(missing_keys)}. Add them to the .env file next "
        "to crew_orchestrator.py."
    )

# CrewAI (via litellm) picks up OPENROUTER_API_KEY from the environment
# automatically when the model string is prefixed with "openrouter/".
LLM_MODEL = os.getenv("CREWAI_MODEL", "openrouter/openai/gpt-4o-mini")
REQUEST_TIMEOUT = 15


# ==========================================
# TOOLS
# ==========================================

def _tavily_search(query: str, max_results: int = 6) -> list[dict]:
    """Shared low-level Tavily call used by both search tools."""
    try:
        request = Request(
            "https://api.tavily.com/search",
            data=json.dumps({
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results,
                "include_domains": [],
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        return [{"url": "", "content": f"Tavily search failed: {e}"}]

    seen, results = set(), []
    for r in data.get("results", []):
        content = r.get("content", "")
        if content and content not in seen:
            seen.add(content)
            results.append({"url": r.get("url", ""), "content": content})
    return results


class TavilyQueryInput(BaseModel):
    query: str = Field(..., description="The search query to run against Tavily.")


class WebSearchTool(BaseTool):
    name: str = "Tavily Web Search"
    description: str = (
        "General web search for a startup idea. Returns recent articles, "
        "news, and pages with URLs and content snippets."
    )
    args_schema: Type[BaseModel] = TavilyQueryInput

    def _run(self, query: str) -> str:
        optimized = build_search_queries(query)["industry"]
        results = _tavily_search(optimized, max_results=6)
        return json.dumps(results, indent=2)


class MarketResearchTool(BaseTool):
    name: str = "Tavily Market Research Search"
    description: str = (
        "Searches specifically for market size, revenue, valuation, and "
        "growth statistics for a given startup idea or business category."
    )
    args_schema: Type[BaseModel] = TavilyQueryInput

    def _run(self, query: str) -> str:
        optimized = build_search_queries(query)["market"]
        results = _tavily_search(optimized, max_results=6)
        return json.dumps(results, indent=2)


class CompetitorRAGTool(BaseTool):
    """
    Competitor Agent tool (Chroma RAG), per the diagram.

    It fetches competitor-focused documents from Tavily, embeds them into a
    fresh in-memory Chroma collection (chromadb's default embedding function,
    no extra API key needed), then retrieves the most relevant chunks for the
    idea. This gives the agent a retrieval step instead of just dumping raw
    search text at the LLM.
    """
    name: str = "Competitor Chroma RAG Search"
    description: str = (
        "Retrieves and semantically ranks competitor/brand information for a "
        "startup idea using a Chroma vector store built from live web results."
    )
    args_schema: Type[BaseModel] = TavilyQueryInput

    def _run(self, query: str) -> str:
        try:
            chromadb = import_module("chromadb")
        except ImportError:
            return (
                "ChromaDB is unavailable. Install the optional dependency with "
                "`pip install chromadb` to enable competitor retrieval."
            )

        docs = _tavily_search(f"{query} top brands competitors alternatives", max_results=8)
        if not docs:
            return "No competitor documents found."

        client = chromadb.EphemeralClient()
        collection = client.get_or_create_collection(name="competitor_docs")

        ids, texts, metadatas = [], [], []
        for i, d in enumerate(docs):
            content = d.get("content", "").strip()
            if not content:
                continue
            ids.append(f"doc-{i}")
            texts.append(content)
            metadatas.append({"url": d.get("url", "")})

        if not texts:
            return "No usable competitor content to index."

        collection.add(ids=ids, documents=texts, metadatas=metadatas)

        query_result = collection.query(query_texts=[f"competitors and brands for {query}"], n_results=min(5, len(texts)))

        retrieved = []
        for doc, meta in zip(query_result.get("documents", [[]])[0], query_result.get("metadatas", [[]])[0]):
            retrieved.append({"url": meta.get("url", ""), "content": doc})

        return json.dumps(retrieved, indent=2)


# ==========================================
# STRUCTURED OUTPUT SCHEMA (Report Generation Agent output)
# ==========================================

class MarketReport(BaseModel):
    market_size: str = Field(..., description="Explicit data-driven metric, valuation, or revenue growth statistics found")
    real_competitors: List[str] = Field(..., description="List of real competitor brand names")
    confidence_score: str = Field(..., description="e.g. '85%'")
    verified_sources: List[str] = Field(..., description="List of source URLs backing the findings")


# ==========================================
# AGENTS
# ==========================================

input_processing_agent = Agent(
    role="Input Processing Agent",
    goal="Turn a raw, possibly vague startup idea into a clean, structured research brief.",
    backstory=(
        "You are the first stage of a market intelligence pipeline. You take messy "
        "user input and normalize it into a precise business category, target "
        "market, and a short list of keywords other agents can search on."
    ),
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

web_search_agent = Agent(
    role="Web Search Agent",
    goal="Find recent, relevant news and general context about the startup idea's industry.",
    backstory="You are a research analyst who scours the live web for current context using Tavily search.",
    tools=[WebSearchTool()],
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

market_research_agent = Agent(
    role="Market Research Agent",
    goal="Find concrete market size, valuation, and growth statistics for the startup idea.",
    backstory="You are a market analyst focused purely on quantitative data: revenue, CAGR, valuations.",
    tools=[MarketResearchTool()],
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

competitor_agent = Agent(
    role="Competitor Agent",
    goal="Identify real, named competitor brands using retrieval-augmented search over live web data.",
    backstory=(
        "You specialize in competitive landscape mapping. You use a Chroma vector "
        "store built on the fly from fresh web results to retrieve the most "
        "relevant competitor mentions rather than relying on raw keyword search."
    ),
    tools=[CompetitorRAGTool()],
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

trend_analysis_agent = Agent(
    role="Trend Analysis Agent",
    goal="Synthesize the web search, market research, and competitor findings into one coherent analysis.",
    backstory=(
        "You are the fan-in point of the pipeline. You reconcile three parallel "
        "research streams, resolve overlaps/conflicts, and produce one unified "
        "narrative with all supporting source URLs preserved."
    ),
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

validation_agent = Agent(
    role="Validation & Scoring Agent",
    goal="Critically evaluate the synthesized research for source agreement, freshness, and reliability.",
    backstory=(
        "You are a skeptical fact-checker. You cross-reference claims across "
        "sources, penalize stale or single-sourced claims, and assign a single "
        "confidence score from 0% to 100%."
    ),
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)

report_agent = Agent(
    role="Report Generation Agent",
    goal="Produce the final, clean, structured JSON report for the frontend.",
    backstory="You format validated findings into the exact schema the UI expects, with no extra commentary.",
    llm=LLM_MODEL,
    verbose=True,
    allow_delegation=False,
)


# ==========================================
# TASKS
# ==========================================

input_processing_task = Task(
    description=(
        "Take this raw startup idea: \"{idea}\".\n"
        "Normalize it into: (1) a clean business category, (2) likely target "
        "market/geography if inferable, (3) 3-5 keywords useful for search. "
        "Keep it concise - this brief is consumed by other agents, not the user."
    ),
    expected_output="A short structured brief: category, target market, keywords.",
    agent=input_processing_agent,
)

# --- Fan-out: these three run in parallel (async_execution=True) ---

web_search_task = Task(
    description=(
        "Using the research brief, search the live web for recent news and "
        "general industry context about: \"{idea}\". Use your search tool."
    ),
    expected_output="A list of relevant findings, each with its source URL, about industry context and news.",
    agent=web_search_agent,
    context=[input_processing_task],
    async_execution=True,
)

market_research_task = Task(
    description=(
        "Using the research brief, find concrete market size, revenue, and "
        "growth statistics for: \"{idea}\". Use your search tool."
    ),
    expected_output="Explicit market size/valuation/growth numbers with source URLs, or a clear note if none were found.",
    agent=market_research_agent,
    context=[input_processing_task],
    async_execution=True,
)

competitor_task = Task(
    description=(
        "Using the research brief, retrieve real, named competitor brands for: "
        "\"{idea}\" using your Chroma RAG search tool. Only list brands that "
        "actually appear in retrieved content - do not invent names."
    ),
    expected_output="A list of real competitor brand names, each with the source URL they were found in.",
    agent=competitor_agent,
    context=[input_processing_task],
    async_execution=True,
)

# --- Fan-in: waits for all three above ---

trend_analysis_task = Task(
    description=(
        "Synthesize the web search, market research, and competitor findings "
        "for \"{idea}\" into one unified analysis. Preserve every source URL "
        "mentioned in the inputs. Note any contradictions between sources."
    ),
    expected_output="One combined narrative covering market context, market size data, and competitors, with all source URLs listed.",
    agent=trend_analysis_agent,
    context=[web_search_task, market_research_task, competitor_task],
)

validation_task = Task(
    description=(
        "Evaluate the synthesized analysis for source agreement and data "
        "freshness. Assign a single confidence score from 0% to 100% based on "
        "how well-supported and current the market size and competitor claims are."
    ),
    expected_output="The synthesized analysis plus a single confidence_score percentage with brief justification.",
    agent=validation_agent,
    context=[trend_analysis_task],
)

report_task = Task(
    description=(
        "Produce the FINAL structured report for \"{idea}\" using the validated "
        "analysis. Return ONLY the fields in the schema - no extra text. "
        "real_competitors must contain only brand names actually found during "
        "research. verified_sources must contain only URLs that were actually "
        "returned by the search tools."
    ),
    expected_output="A JSON object with market_size, real_competitors, confidence_score, and verified_sources.",
    agent=report_agent,
    context=[validation_task],
    output_pydantic=MarketReport,
)


# ==========================================
# CREW (the Orchestrator)
# ==========================================

def build_crew() -> Crew:
    return Crew(
        agents=[
            input_processing_agent,
            web_search_agent,
            market_research_agent,
            competitor_agent,
            trend_analysis_agent,
            validation_agent,
            report_agent,
        ],
        tasks=[
            input_processing_task,
            web_search_task,
            market_research_task,
            competitor_task,
            trend_analysis_task,
            validation_task,
            report_task,
        ],
        process=Process.sequential,
        verbose=True,
    )


def run_market_analysis(idea: str) -> dict:
    """
    Kicks off the full crew for a given idea and returns a plain dict matching
    the schema the frontend expects.
    """
    crew = build_crew()
    result = crew.kickoff(inputs={"idea": idea})

    if result.pydantic:
        return result.pydantic.model_dump()

    # Fallback: try to parse whatever text came back as JSON.
    try:
        return json.loads(result.raw)
    except (json.JSONDecodeError, TypeError):
        return {
            "market_size": "Could not parse structured output.",
            "real_competitors": [],
            "confidence_score": "0%",
            "verified_sources": [],
        }


if __name__ == "__main__":
    idea = input("Enter Startup Idea: ").strip()
    output = run_market_analysis(idea)
    print(json.dumps(output, indent=2))
