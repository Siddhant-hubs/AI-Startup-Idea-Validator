# Agile / Project Management Document

## Product Backlog

| ID | User Story | Priority | Status |
|---|---|---|---|
| US-01 | As a founder, I want market validation for my idea. | Must | Done |
| US-02 | As a founder, I want SWOT and risk analysis. | Must | Done |
| US-03 | As a founder, I want MVP features prioritized by MoSCoW. | Must | Done |
| US-04 | As a founder, I want a GTM strategy. | Must | Done |
| US-05 | As a founder, I want to ask follow-up questions. | Must | Done |
| US-06 | As a founder, I want a downloadable validation report. | Must | Done |
| US-07 | As a developer, I want E2E tests. | Must | Done |
| US-08 | As a developer, I want optimized search queries and prompts. | Should | Done |
| US-09 | As a reviewer, I want technical documentation. | Should | Done |
| US-10 | As a team, I want a demo presentation and Q/A notes. | Should | Done |

## Sprint / Milestone Plan

### Milestone 3 — Weeks 5–6
- SWOT and risk agent.
- MVP recommendation agent.
- GTM strategy agent.
- Conversational startup advisor.

### Milestone 4 — Weeks 7–8
- Report generation agent.
- E2E testing.
- Search/prompt optimization.
- Accuracy/quality checks.
- Technical and project documentation.
- Demo preparation.

## Definition of Done

A feature is considered done when:

- Its Python module is integrated into the API workflow.
- The frontend can consume its output where applicable.
- Structured output has a defined contract.
- Error handling exists.
- Relevant automated tests exist.
- Documentation is updated.

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| LLM structured output is malformed | Explicit schema + parsing + contract checks |
| Web search returns weak sources | Intent-specific queries + source URLs |
| External API failure | HTTP error handling + user-visible errors |
| Repeated expensive validation | Session cache |
| Strategy output treated as fact | Report disclaimer + source references |

## Retrospective

### What worked
- Modular specialist agents.
- Explicit JSON contracts.
- Context passed between stages.
- Mocked E2E tests for external services.

### What to improve
- Persistent report history.
- Automated factual claim verification.
- Production observability.
- Deployment automation.
