"""Milestone 4 — mocked end-to-end API tests.

Every external/paid call (market research, SWOT/MVP/GTM LLM agents) is
mocked so this suite runs offline and does not consume API credits.
Only report generation (local ReportLab) and quality scoring
(deterministic) run for real.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


MOCK_MARKET = {
    "market_size": "$2B by 2028",
    "confidence_score": 0.75,
    "real_competitors": ["Competitor A", "Competitor B"],
    "verified_sources": ["https://example.com/a", "https://example.com/b"],
}

MOCK_SWOT = {
    "swot": {
        "strengths": ["Fast iteration"],
        "weaknesses": ["Small team"],
        "opportunities": ["Growing market"],
        "threats": ["Well-funded incumbents"],
    },
    "risk_analysis": {"high_risks": [], "medium_risks": [], "low_risks": []},
    "competitor_risk": {"market_saturation": "medium"},
    "market_demand_prediction": {"demand_level": "high"},
    "overall_risk_score": "5/10",
    "summary": "Solid idea with manageable risk.",
}

MOCK_MVP = {
    "moscow_framework": {
        "must_have": [{"feature": "Core flow", "reason": "Core value", "effort": "medium", "impact": "high"}],
        "should_have": [],
        "could_have": [],
        "wont_have": [],
    },
    "mvp_summary": "Ship the core flow first.",
}

MOCK_GTM = {
    "positioning": {"value_proposition": "Simple and fast"},
    "channels": {"primary": [], "secondary": []},
    "customer_acquisition": {"first_100_customers": "Community outreach"},
    "pricing_strategy": {"model": "freemium"},
    "launch_plan": {},
    "growth_metrics": {},
    "gtm_summary": "Grow via community first.",
}

MOCK_CHAT_REPLY = {
    "answer": "Focus on your highest-impact must-have feature first.",
    "follow_up_suggestions": ["What should our pricing be?"],
    "confidence": "high",
    "referenced_sections": ["MVP"],
}


@pytest.fixture
def client():
    """Import the app fresh per-test so caches (_market_cache, _validation_cache) start clean."""
    import importlib
    import web_search_agent

    importlib.reload(web_search_agent)
    return TestClient(web_search_agent.app)


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["milestone"] == "4"


def test_validate_rejects_short_idea(client):
    r = client.post("/api/validate", json={"idea": "ab"})
    assert r.status_code == 422  # pydantic min_length violation


@patch("web_search_agent.run_gtm_analysis", return_value=MOCK_GTM)
@patch("web_search_agent.run_mvp_analysis", return_value=MOCK_MVP)
@patch("web_search_agent.run_swot_risk_analysis", return_value=MOCK_SWOT)
@patch("web_search_agent.run_market_analysis", return_value=MOCK_MARKET)
def test_validate_full_pipeline(mock_market, mock_swot, mock_mvp, mock_gtm, client):
    r = client.post("/api/validate", json={"idea": "AI tutor for engineering students"})
    assert r.status_code == 200
    data = r.json()

    assert data["startup_idea"] == "AI tutor for engineering students"
    assert data["market_validation"] == MOCK_MARKET
    assert data["swot_analysis"] == MOCK_SWOT
    assert data["mvp_features"] == MOCK_MVP
    assert data["gtm_strategy"] == MOCK_GTM
    assert data["chatbot"]["ready"] is True

    mock_market.assert_called_once()
    mock_swot.assert_called_once()
    mock_mvp.assert_called_once()
    mock_gtm.assert_called_once()


@patch("web_search_agent.run_gtm_analysis", return_value=MOCK_GTM)
@patch("web_search_agent.run_mvp_analysis", return_value=MOCK_MVP)
@patch("web_search_agent.run_swot_risk_analysis", return_value=MOCK_SWOT)
@patch("web_search_agent.run_market_analysis", return_value=MOCK_MARKET)
def test_validate_uses_cache_on_second_call(mock_market, mock_swot, mock_mvp, mock_gtm, client):
    idea = "AI tutor for engineering students"
    r1 = client.post("/api/validate", json={"idea": idea})
    r2 = client.post("/api/validate", json={"idea": idea})

    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()
    # Second call must be served from cache: agents should only run once.
    mock_market.assert_called_once()
    mock_swot.assert_called_once()
    mock_mvp.assert_called_once()
    mock_gtm.assert_called_once()


@patch("web_search_agent.run_market_analysis", side_effect=RuntimeError("Tavily unavailable"))
def test_validate_pipeline_failure_returns_500(mock_market, client):
    r = client.post("/api/validate", json={"idea": "A brand new untested idea"})
    assert r.status_code == 500
    assert "Validation pipeline failed" in r.json()["detail"]


@patch("web_search_agent.run_chatbot_query", return_value=MOCK_CHAT_REPLY)
def test_chat_endpoint(mock_chat, client):
    r = client.post(
        "/api/chat",
        json={
            "question": "Which MVP feature should we build first?",
            "startup_idea": "AI tutor for engineering students",
            "conversation_history": [],
        },
    )
    assert r.status_code == 200
    assert r.json() == MOCK_CHAT_REPLY
    mock_chat.assert_called_once()


def test_chat_rejects_empty_question(client):
    r = client.post("/api/chat", json={"question": "   "})
    assert r.status_code == 400


def test_report_requires_startup_idea(client):
    r = client.post("/api/report", json={"market_validation": {}})
    assert r.status_code == 400


def test_report_generates_downloadable_pdf(client):
    validation = {
        "startup_idea": "AI tutor for engineering students",
        "market_validation": MOCK_MARKET,
        "swot_analysis": MOCK_SWOT,
        "mvp_features": MOCK_MVP,
        "gtm_strategy": MOCK_GTM,
    }
    r = client.post("/api/report", json=validation)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"


def test_quality_check_endpoint_scores_valid_payload(client):
    validation = {
        "market_validation": {
            "market_size": "x", "real_competitors": [], "confidence_score": 1, "verified_sources": [],
        },
        "swot_analysis": {
            "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
            "risk_analysis": {},
        },
        "mvp_features": {
            "moscow_framework": {"must_have": [], "should_have": [], "could_have": [], "wont_have": []},
        },
        "gtm_strategy": {
            "positioning": {}, "channels": {}, "customer_acquisition": {},
            "pricing_strategy": {}, "launch_plan": {}, "growth_metrics": {},
        },
    }
    r = client.post("/api/quality-check", json=validation)
    assert r.status_code == 200
    body = r.json()
    assert body["accuracy_score"] == 100.0
    assert 0.0 <= body["accuracy_score"] <= 100.0


def test_knowledge_base_status_endpoint(client):
    r = client.get("/api/knowledge-base")
    assert r.status_code == 200
    assert "ready" in r.json()
