"""Compatibility entry point for the AI Startup Idea Validator FastAPI application."""

from web_search_agent import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8900, reload=True)
