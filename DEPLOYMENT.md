# Deployment Guide

## Local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python web_search_agent.py
```

Open `http://127.0.0.1:8900`.

## Production checklist

1. Put `TAVILY_API_KEY` and `OPENROUTER_API_KEY` in the hosting provider's secret manager.
2. Never commit `.env`.
3. Run Uvicorn behind HTTPS/reverse proxy.
4. Restrict CORS to the real frontend origin.
5. Add rate limiting and authentication.
6. Persist reports and project history.
7. Add logs/metrics and error tracking.
8. Set a production `CREWAI_MODEL` if required.

## Example production command

```bash
uvicorn web_search_agent:app --host 0.0.0.0 --port 8900
```

A live deployed URL is environment-specific and cannot be truthfully supplied until the project is deployed to a hosting provider.
