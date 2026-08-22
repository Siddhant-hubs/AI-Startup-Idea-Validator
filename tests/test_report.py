"""Milestone 4 — report generation tests.

Exercises the real ReportLab pipeline (no mocking needed: PDF generation
is local and deterministic) and checks a valid PDF file is produced.
"""

import os
import tempfile

from report_agent import StartupValidationReportAgent


SAMPLE_VALIDATION = {
    "startup_idea": "AI tutor for engineering students",
    "market_validation": {
        "market_size": "$2.1B by 2027",
        "confidence_score": "0.82",
        "real_competitors": ["Chegg", "Course Hero"],
        "verified_sources": ["https://example.com/report"],
    },
    "swot_analysis": {
        "swot": {
            "strengths": ["Personalized learning"],
            "weaknesses": ["High LLM cost"],
            "opportunities": ["STEM tutoring demand"],
            "threats": ["Free alternatives"],
        },
        "risk_analysis": {
            "high_risks": [
                {"risk": "Content accuracy", "description": "Wrong answers", "mitigation": "Human review"}
            ],
            "medium_risks": [],
            "low_risks": [],
        },
        "competitor_risk": {"market_saturation": "medium"},
        "market_demand_prediction": {"demand_level": "high"},
        "overall_risk_score": "6/10",
        "summary": "Solid opportunity with moderate competitive risk.",
    },
    "mvp_features": {
        "moscow_framework": {
            "must_have": [
                {"feature": "Chat tutor", "reason": "Core value", "effort": "medium", "impact": "high"}
            ],
            "should_have": [],
            "could_have": [],
            "wont_have": [],
        },
        "tech_stack_recommendation": {"frontend": "React", "backend": "FastAPI"},
        "mvp_timeline": {"phase_1": {"duration": "4 weeks", "focus": "Core chat"}},
        "resource_requirements": {"team_size": "2-3", "budget_estimate": "$10k-$20k", "key_roles": ["PM"]},
        "success_metrics": ["Weekly active users"],
        "mvp_summary": "Ship a focused chat tutor first.",
    },
    "gtm_strategy": {
        "positioning": {"value_proposition": "Affordable 1:1 tutoring, on demand"},
        "channels": {
            "primary": [{"channel": "TikTok", "strategy": "Study tips", "cost": "low"}],
            "secondary": [],
        },
        "customer_acquisition": {
            "first_100_customers": "University Discord communities",
            "first_1000_customers": "Referral program",
        },
        "pricing_strategy": {"model": "freemium"},
        "launch_plan": {"pre_launch": {"duration": "2 weeks", "activities": ["Waitlist"]}},
        "growth_metrics": {"month_1_target": "500 users"},
        "gtm_summary": "Grow through campus communities before paid acquisition.",
    },
}


def test_generate_report_creates_valid_pdf_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = StartupValidationReportAgent(output_dir=tmp_dir)
        path = agent.generate(SAMPLE_VALIDATION)

        assert os.path.exists(path)
        assert path.endswith(".pdf")
        assert os.path.getsize(path) > 0

        with open(path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"


def test_generate_report_filename_is_derived_from_idea():
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = StartupValidationReportAgent(output_dir=tmp_dir)
        path = agent.generate(SAMPLE_VALIDATION)
        assert "ai-tutor-for-engineering-students" in os.path.basename(path).lower()


def test_generate_report_handles_missing_sections_gracefully():
    """Report generation must not crash when upstream agent output is incomplete."""
    minimal = {"startup_idea": "Minimal idea with no other data"}
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = StartupValidationReportAgent(output_dir=tmp_dir)
        path = agent.generate(minimal)
        assert os.path.exists(path)
        with open(path, "rb") as f:
            assert f.read(5) == b"%PDF-"
