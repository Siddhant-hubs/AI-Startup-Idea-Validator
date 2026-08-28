# Project Report
## AI Startup Idea Validator

### Abstract

AI Startup Idea Validator is an AI-assisted decision-support platform for early-stage startup validation. A user supplies a startup concept, after which the system performs live market research and routes the result through specialized strategy agents. The final Milestone 4 system combines market validation, SWOT/risk analysis, MVP prioritization, Go-To-Market strategy, conversational follow-up and downloadable reporting.

### Problem Statement

Early-stage founders often need to evaluate market demand, competition, product scope and launch strategy before committing significant resources. These activities are time-consuming when performed manually and can become inconsistent when different analyses are not connected.

### Objectives

- Research market conditions using live web search.
- Identify real competitors and relevant market evidence.
- Produce structured SWOT and risk analysis.
- Prioritize MVP features using MoSCoW.
- Generate a practical Go-To-Market strategy.
- Support follow-up questions through a startup advisor.
- Compile the complete analysis into a downloadable PDF.
- Test the main workflow and validate structured outputs.

### Methodology

The architecture follows a modular agent pipeline. Market research is performed through a CrewAI fan-out/fan-in workflow. Specialist agents then consume relevant context from earlier stages. Structured JSON is used between machine-readable stages. The report agent compiles the final structured result without adding unsupported facts.

### Technology Stack

- Python
- FastAPI
- CrewAI
- OpenRouter-compatible LLM
- Tavily Search API
- ChromaDB for competitor retrieval
- ReportLab for PDF generation
- HTML/CSS/JavaScript frontend
- Pytest for automated testing

### Milestone 3 Work

The Milestone 3 workflow added SWOT/Risk, MVP/MoSCoW, GTM and the conversational advisor. The outputs are connected in sequence and ingested into the advisor knowledge base.

### Milestone 4 Work

Milestone 4 adds:

1. Startup Validation Report Generation Agent.
2. Downloadable PDF output.
3. End-to-end and contract tests.
4. Search query optimization.
5. Prompt-engineering documentation.
6. Deterministic output quality checks.
7. Technical documentation.
8. Project/Agile/demo documentation.
9. MIT license.

### Results

The system now provides one integrated validation workflow rather than isolated agent outputs. The frontend exposes the market, SWOT/Risk, MVP/MoSCoW, GTM and advisor views and provides a PDF download after successful validation.

### Limitations

LLM strategy outputs are recommendations. Market claims must be checked against their cited sources. The current chatbot knowledge base is in-memory and therefore session-scoped. A production system should add persistent storage, authentication, rate limiting, observability and stronger factual verification.

### Future Scope

- Persistent user/report storage.
- User accounts and project history.
- Source-level claim verification.
- Multi-language reports.
- PDF templates and charts.
- Deployment with HTTPS and secret management.
- Evaluation datasets for factual accuracy and agent consistency.
