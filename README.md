# AI Startup Idea Validator — Milestones 3 & 4

An AI-powered startup validation platform that combines live market research with LLM-based SWOT/risk analysis, MVP MoSCoW prioritization, Go-To-Market strategy generation, and a conversational startup advisor.

## Milestone 3 coverage

1. **SWOT & Risk Analysis Agent**
   - Strengths, weaknesses, opportunities and threats.
   - High/medium/low risks with mitigation.
   - Competitor risk and differentiation.
   - Market-demand prediction and overall risk score.

2. **MVP Feature Recommendation Agent**
   - MoSCoW: Must Have, Should Have, Could Have, Won't Have.
   - Effort and impact for feature prioritization.
   - Tech-stack recommendation.
   - MVP timeline, team/budget and success metrics.

3. **Go-To-Market Strategy Agent**
   - Positioning and value proposition.
   - Primary/secondary acquisition channels.
   - First 100 and first 1000 customer strategy.
   - Pricing, launch plan, partnerships and growth targets.

4. **Conversational Startup Advisor**
   - Validation outputs are ingested into an in-memory knowledge base.
   - Follow-up questions use SWOT, MVP and GTM results.
   - Conversation history is passed to the advisor.
   - Suggested follow-up questions are returned by the chatbot.

## Architecture

```text
Startup Idea
    |
    v
FastAPI
    |
    +--> Market Validation Crew
    |       +--> Web Search
    |       +--> Market Research
    |       +--> Competitor Chroma RAG
    |       +--> Trend Analysis
    |       +--> Validation / Scoring
    |       +--> Report Generation
    |
    v
SWOT + Risk Agent
    |
    v
MVP / MoSCoW Agent
    |
    v
GTM Strategy Agent
    |
    v
Knowledge Base Ingestion
    |
    v
Conversational Startup Advisor
```

The original market pipeline already uses CrewAI fan-out/fan-in research, Tavily web search, Chroma retrieval and structured report generation. Milestone 3 adds the downstream validation layers and chatbot on top of that pipeline.

## Setup

### 1. Python

Python 3.9+ is recommended.

```bash
python --version
```

### 2. Virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies

```bash
pip install -r requirements.txt
```

### 4. API keys

Copy `.env.example` to `.env` and add your own Tavily and OpenRouter keys.

```env
TAVILY_API_KEY=your_tavily_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

**Never commit `.env` to GitHub.** `.gitignore` already excludes it.

## Run

Start the server:

```bash
python web_search_agent.py
```

Then open:

```text
http://127.0.0.1:8900
```

The frontend is served directly by FastAPI, so there is no need to double-click `index.html`.

## API endpoints

### Health

```http
GET /health
```

### Full Milestone 3 validation

```http
POST /api/validate
Content-Type: application/json

{
  "idea": "AI tutor for engineering students"
}
```

Returns:

```json
{
  "startup_idea": "...",
  "market_validation": {},
  "swot_analysis": {},
  "mvp_features": {},
  "gtm_strategy": {},
  "chatbot": {
    "ready": true,
    "knowledge_base_sections": [
      "startup_idea",
      "swot_analysis",
      "mvp_features",
      "gtm_strategy"
    ]
  }
}
```

### Chatbot

```http
POST /api/chat
Content-Type: application/json

{
  "question": "Which MVP feature should we build first?",
  "startup_idea": "AI tutor for engineering students",
  "conversation_history": []
}
```

### Knowledge-base status

```http
GET /api/knowledge-base
```

## CLI test

With the server running:

```bash
python appp.py
```

## Demo flow for Milestone 3

Use a single idea and demonstrate these five steps:

1. Enter the idea and run **Full Validation**.
2. Open **SWOT & Risk** and explain the four SWOT categories plus risk levels.
3. Open **MVP / MoSCoW** and explain why Must/Should/Could/Won't features are prioritized.
4. Open **Go-To-Market** and show positioning, channels, first-100/first-1000 acquisition, pricing and launch plan.
5. Open **Advisor Chat** and ask follow-ups such as:
   - Which risk should we mitigate first?
   - Which MVP feature should we build first?
   - How do we get our first 100 customers?
   - What should our pricing test look like?

## Notes

- The current knowledge base is **in-memory** and lasts for the running server session.
- The market research pipeline depends on live Tavily access and an OpenRouter-compatible LLM.
- LLM-generated market predictions and strategic recommendations should be presented as analysis, not guaranteed facts.

## Demo checklist
See `MILESTONE3_DEMO.md` for the exact presentation/demo sequence.

## Important CrewAI/OpenRouter compatibility fix

The Milestone 3 agents (`swot_risk_agent.py`, `mvp_agent.py`, `gtm_agent.py`, and `chatbot_agent.py`) use the CrewAI-compatible model string `openrouter/openai/gpt-4o-mini`. This is intentional: current CrewAI validation expects the Agent `llm` value to be a model string or a CrewAI `BaseLLM`; passing a LangChain `ChatOpenAI` instance can produce a Pydantic validation error.

The model can be changed with:

```env
CREWAI_MODEL=openrouter/openai/gpt-4o-mini
```

If `.env` does not define it, the above model is used automatically.


## Milestone 4 additions

- `report_agent.py` — downloadable PDF validation report
- `search_optimization.py` — intent-specific web query construction
- `quality_checks.py` — deterministic output-contract checks
- `tests/` — contract, report and mocked E2E tests
- `TECHNICAL_DOCUMENTATION.md` — technical architecture and APIs
- `PROJECT_REPORT.md` — project report
- `AGILE_DOCUMENT.md` — Agile backlog, risks and retrospective
- `MILESTONE4_DEMO.md` — final demo and Q/A script
- `DEPLOYMENT.md` — local/production deployment guide

### Download report
After validation, click **Download Validation PDF** in the frontend. The PDF combines market validation, SWOT/risk, MVP/MoSCoW, GTM and advisor context.

### Tests
Run `python run_tests.py`. External LLM/Tavily calls are mocked in the E2E test so the test suite does not consume API credits.
