# Milestone 3 Demo Checklist

1. Start server: `python web_search_agent.py`
2. Open: `http://127.0.0.1:8900`
3. Enter one startup idea.
4. Click **Run Full Validation**.
5. Demonstrate the five tabs:
   - Market: live market/competitor validation
   - SWOT & Risk: strengths, weaknesses, opportunities, threats and risk mitigation
   - MVP / MoSCoW: Must/Should/Could/Won't + effort/impact
   - Go-To-Market: positioning, channels, first 100/1000 customers, pricing and launch
   - Advisor Chat: follow-up questions grounded in the generated validation data
6. Suggested live questions:
   - Which risk should we mitigate first?
   - Which MVP feature should we build first?
   - How can we get our first 100 customers?
   - What pricing should we test?

The `/api/validate` endpoint executes Market -> SWOT -> MVP -> GTM -> Knowledge Base ingestion as one integrated workflow.
