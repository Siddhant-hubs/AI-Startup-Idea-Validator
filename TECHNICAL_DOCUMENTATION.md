# Technical Documentation — AI Startup Idea Validator

## 1. System Objective

The system evaluates a startup idea through live market research and a sequence of LLM-based strategy agents. Milestone 3 added SWOT/Risk, MVP/MoSCoW, GTM and the conversational advisor. Milestone 4 adds report generation, automated quality checks, end-to-end tests, and search/prompt optimization.

## 2. Architecture

```text
Browser
  |
  | POST /api/validate
  v
FastAPI
  |
  +--> Market Validation Crew
  |      +--> Input processing
  |      +--> Tavily industry search
  |      +--> Tavily market search
  |      +--> Competitor retrieval
  |      +--> Trend synthesis
  |      +--> Validation/scoring
  |
  +--> SWOT & Risk Agent
  |
  +--> MVP / MoSCoW Agent
  |
  +--> GTM Strategy Agent
  |
  +--> Knowledge Base ingestion
  |
  +--> Report Generation Agent --> PDF
  |
  +--> Conversational Advisor
```

## 3. Components

### Market Validation
`crew_orchestrator.py` uses a fan-out/fan-in CrewAI workflow. Research streams are performed in parallel and then synthesized before validation/scoring.

### SWOT/Risk
`swot_risk_agent.py` consumes the market result and produces four SWOT quadrants, high/medium/low risks, competitor risk, demand prediction and an overall risk score.

### MVP/MoSCoW
`mvp_agent.py` consumes SWOT context and prioritizes features into Must Have, Should Have, Could Have and Won't Have. It also produces technology, timeline, resource and success-metric recommendations.

### GTM
`gtm_agent.py` consumes SWOT and MVP context and generates positioning, channels, customer acquisition, pricing, launch, partnerships and growth targets.

### Conversational Advisor
`chatbot_agent.py` ingests the validation outputs into an in-memory knowledge base. Follow-up questions use this context and recent conversation history.

### Report Generation
`report_agent.py` is a deterministic report-generation agent/compiler. It accepts the structured outputs and produces a multi-section PDF using ReportLab. It does not fabricate missing facts.

### Quality Checks
`quality_checks.py` validates output contracts and returns a simple accuracy/quality score. This is a structural check, not a claim of factual truth.

## 4. API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Frontend |
| GET | `/health` | Service/component health |
| POST | `/api/search-agent` | Original market endpoint |
| POST | `/api/validate` | Full Milestone 3/4 pipeline |
| POST | `/api/chat` | Conversational advisor |
| POST | `/api/report` | Download PDF |
| POST | `/api/quality-check` | Output-contract quality check |
| GET | `/api/knowledge-base` | Current KB status |

## 5. Search Query Optimization

The `search_optimization.py` module creates intent-specific queries for:

- industry/trends/news
- market size/revenue/growth
- competitors/alternatives
- customers/pain points/use cases

This reduces vague searches and makes downstream evidence more relevant.

## 6. Prompt Engineering

The project uses structured-output prompts with explicit JSON schemas. Each specialist receives the previous agent's relevant context instead of the entire raw workflow. This reduces ambiguity and keeps responsibilities separated.

Recommended prompt rules:

1. Define the role and decision objective.
2. Provide only relevant context.
3. Specify an exact output schema.
4. Require JSON only for machine-readable stages.
5. Require evidence/source URLs for market claims.
6. Mark predictions as estimates rather than facts.
7. Pass outputs downstream explicitly.

## 7. Error Handling

- API validation rejects empty/short ideas.
- Backend converts pipeline exceptions into HTTP 500 responses with a useful detail message.
- Report generation validates that a startup idea exists.
- Frontend displays errors rather than silently failing.
- Cached validation results prevent unnecessary repeat calls for the same idea during a server session.

## 8. Testing Strategy

`tests/test_contracts.py` checks deterministic query and output schemas.

`tests/test_report.py` verifies PDF creation.

`tests/test_api_e2e.py` mocks external AI agents and exercises `/api/validate` and `/api/report` end-to-end without consuming API credits.

Run:

```bash
python run_tests.py
```

## 9. Limitations

The quality score validates structure and completeness. It does not independently verify every market claim. Live market information should be checked against the returned source URLs.

The chatbot knowledge base is session-memory only. A production deployment should persist reports and embeddings in a durable store.
