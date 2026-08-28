"""Compatibility entry point for the AI Startup Idea Validator FastAPI application."""

import os

from web_search_agent import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8900))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=bool(os.environ.get("DEV_RELOAD")))