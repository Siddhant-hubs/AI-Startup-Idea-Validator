# Milestone 4 Demo Script

## Demo sequence (5–7 minutes)

### 1. Open the application
Start:

```bash
python web_search_agent.py
```

Open `http://127.0.0.1:8900`.

### 2. Enter an idea
Example:

`AI tutor for engineering students`

Click **Run Full Validation**.

### 3. Show Market
Explain:
- market-size evidence
- confidence score
- real competitors
- source URLs

### 4. Show SWOT & Risk
Explain one strength, one weakness, one opportunity, one threat and the highest-priority risk/mitigation.

### 5. Show MVP / MoSCoW
Explain why one feature is Must Have and why another is deferred.

### 6. Show GTM
Explain positioning, first 100 customers, acquisition channels and pricing.

### 7. Download PDF
Click **Download Validation PDF** and open the generated report.

### 8. Ask the advisor
Ask:
- Which risk should we mitigate first?
- Which MVP feature should we build first?
- How do we get our first 100 customers?

### 9. Testing
Run:

```bash
python run_tests.py
```

### Q/A points

**Why CrewAI?** Modular agent orchestration and explicit context passing.

**Why Tavily?** Live web search for current market evidence.

**Why MoSCoW?** It gives a simple resource-aware MVP prioritization framework.

**Is the AI output guaranteed to be correct?** No. Market claims should be checked against source URLs; strategy outputs are decision support.

**What is the current limitation?** Chatbot knowledge is session-scoped and deployment still requires hosting configuration and secure secret management.
