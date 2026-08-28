"""
AI Startup Idea Validator — Backend (Milestone 3 + Milestone 4)
----------------------------------------------------------------
FastAPI server exposing:
- POST /api/search-agent   : backward-compatible market research
- POST /api/validate       : full Market -> SWOT -> MVP -> GTM validation pipeline
- POST /api/chat           : conversational startup advisor
- POST /api/report         : downloadable PDF validation report
- POST /api/quality-check  : deterministic output-contract quality score
- GET  /api/knowledge-base : chatbot KB status
- GET  /health             : health check
- GET  /                   : frontend
"""

import os
import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from crew_orchestrator import run_market_analysis
from swot_risk_agent import run_swot_risk_analysis
from mvp_agent import run_mvp_analysis
from gtm_agent import run_gtm_analysis
from chatbot_agent import ingest_knowledge, run_chatbot_query, get_knowledge_base
from report_agent import generate_validation_report
from quality_checks import score_validation

app = FastAPI(
    title="AI Startup Idea Validator",
    version="4.0.0",
    description="Market validation, SWOT/Risk, MVP, GTM, advisor chatbot and downloadable validation reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_market_cache: dict[str, dict] = {}
_validation_cache: dict[str, dict] = {}


class IdeaRequest(BaseModel):
    idea: str = Field(..., min_length=3)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    startup_idea: str = ""
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


def _clean_idea(idea: str) -> str:
    value = idea.strip()
    if len(value) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please enter a concrete startup concept or business category.",
        )
    return value


def _safe_json(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except TypeError:
        return str(data)


def _run_market(idea: str) -> dict:
    key = idea.lower()
    if key not in _market_cache:
        _market_cache[key] = run_market_analysis(idea)
    return _market_cache[key]


@app.get("/")
def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Backend is running. index.html was not found."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "milestone": "4",
        "components": [
            "market_validation",
            "swot_risk",
            "mvp_moscow",
            "go_to_market",
            "startup_advisor_chatbot",
            "report_generation",
            "e2e_testing",
            "search_prompt_optimization",
        ],
    }


@app.post("/api/search-agent")
def search_agent(payload: IdeaRequest):
    """Backward-compatible endpoint used by the original market validator."""
    idea = _clean_idea(payload.idea)
    try:
        return _run_market(idea)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Market pipeline failed: {exc}") from exc


@app.post("/api/validate")
def validate_startup(payload: IdeaRequest):
    """
    Full validation pipeline:
      1. Live market/competitor validation
      2. SWOT + risk analysis
      3. MVP MoSCoW recommendations
      4. Go-To-Market strategy
      5. Knowledge-base ingestion for chatbot follow-ups
    """
    idea = _clean_idea(payload.idea)
    key = idea.lower()

    if key in _validation_cache:
        cached = _validation_cache[key]
        ingest_knowledge(
            idea,
            cached.get("swot_analysis"),
            cached.get("mvp_features"),
            cached.get("gtm_strategy"),
        )
        return cached

    try:
        market = _run_market(idea)

        swot = run_swot_risk_analysis(
            idea,
            market_context=_safe_json(market),
        )

        mvp = run_mvp_analysis(
            idea,
            swot_context=_safe_json(swot),
        )

        gtm = run_gtm_analysis(
            idea,
            swot_context=_safe_json(swot),
            mvp_context=_safe_json(mvp),
        )

        ingest_knowledge(
            startup_idea=idea,
            swot_data=swot,
            mvp_data=mvp,
            gtm_data=gtm,
        )

        result = {
            "startup_idea": idea,
            "market_validation": market,
            "swot_analysis": swot,
            "mvp_features": mvp,
            "gtm_strategy": gtm,
            "chatbot": {
                "ready": True,
                "knowledge_base_sections": [
                    "startup_idea",
                    "swot_analysis",
                    "mvp_features",
                    "gtm_strategy",
                ],
            },
        }
        _validation_cache[key] = result
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Validation pipeline failed: {exc}",
        ) from exc


@app.post("/api/chat")
def chat(payload: ChatRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        return run_chatbot_query(
            user_question=question,
            startup_idea=payload.startup_idea,
            conversation_history=payload.conversation_history,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chatbot failed: {exc}") from exc


@app.post("/api/report")
def create_report(payload: dict[str, Any]):
    """Generate a downloadable PDF from a completed validation result."""
    validation = payload
    if not validation.get("startup_idea"):
        raise HTTPException(status_code=400, detail="Validation result must include startup_idea.")
    try:
        report_path = generate_validation_report(validation)
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=os.path.basename(report_path),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc


@app.post("/api/quality-check")
def quality_check(payload: dict[str, Any]):
    """Return deterministic output-contract/accuracy checks for a validation result."""
    return score_validation(payload)


@app.get("/api/knowledge-base")
def knowledge_base_status():
    kb = get_knowledge_base()
    return {
        "ready": bool(kb),
        "startup_idea": kb.get("startup_idea", ""),
        "sections": [key for key in kb.keys() if key != "startup_idea"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_search_agent:app", host="127.0.0.1", port=8900, reload=True)
