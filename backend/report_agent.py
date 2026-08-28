"""Milestone 4 — Startup Validation Report Generation Agent.

Compiles all validation outputs into a structured, downloadable PDF.
The report compiler is deterministic: it formats already-generated agent
outputs and never invents missing facts.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


class StartupValidationReportAgent:
    """Compile Market, SWOT, MVP, GTM and chatbot readiness into a PDF."""

    def __init__(self, output_dir: str | None = None):
        self.output_dir = Path(output_dir or Path(__file__).parent / "generated_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _text(value: Any) -> str:
        if value is None:
            return "Not provided"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)

    @staticmethod
    def _safe_filename(idea: str) -> str:
        base = re.sub(r"[^a-zA-Z0-9]+", "-", idea.strip()).strip("-").lower() or "startup"
        return f"startup-validation-{base[:60]}.pdf"

    def _styles(self):
        styles = getSampleStyleSheet()
        return {
            "title": ParagraphStyle("ReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=24, leading=28, spaceAfter=12),
            "subtitle": ParagraphStyle("Subtitle", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, textColor=colors.grey, spaceAfter=20),
            "h1": ParagraphStyle("H1", parent=styles["Heading1"], fontSize=17, leading=21, spaceBefore=10, spaceAfter=8),
            "h2": ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=7, spaceAfter=5),
            "body": ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=14, spaceAfter=5),
            "small": ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, leading=11, textColor=colors.grey),
        }

    def _p(self, text: Any, style) -> Paragraph:
        clean = self._text(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
        return Paragraph(clean, style)

    def _bullets(self, items: list[Any], style):
        return [self._p(f"• {self._text(item)}", style) for item in items] or [self._p("• Not provided", style)]

    def generate(self, validation: dict[str, Any]) -> str:
        idea = validation.get("startup_idea", "Startup idea")
        filename = self._safe_filename(idea)
        path = self.output_dir / filename
        styles = self._styles()
        doc = SimpleDocTemplate(
            str(path), pagesize=A4,
            rightMargin=16*mm, leftMargin=16*mm,
            topMargin=16*mm, bottomMargin=16*mm,
            title=f"Startup Validation Report — {idea}",
            author="AI Startup Idea Validator",
        )

        market = validation.get("market_validation") or {}
        swot = validation.get("swot_analysis") or {}
        mvp = validation.get("mvp_features") or {}
        gtm = validation.get("gtm_strategy") or {}
        story = []

        story += [self._p("AI Startup Validation Report", styles["title"]),
                  self._p(idea, styles["subtitle"]),
                  self._p(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["small"]), Spacer(1, 10)]

        story.append(self._p("1. Executive Summary", styles["h1"]))
        summary = swot.get("summary") or gtm.get("gtm_summary") or mvp.get("mvp_summary") or "See the detailed sections below."
        story.append(self._p(summary, styles["body"]))
        story.append(self._p(f"Market confidence: {market.get('confidence_score', 'Not provided')}", styles["body"]))
        story.append(self._p(f"Overall risk score: {swot.get('overall_risk_score', 'Not provided')}", styles["body"]))

        story.append(self._p("2. Market Validation", styles["h1"]))
        story.append(self._p(f"Market size: {market.get('market_size', 'Not provided')}", styles["body"]))
        story.append(self._p(f"Confidence: {market.get('confidence_score', 'Not provided')}", styles["body"]))
        story.append(self._p("Real competitors", styles["h2"]))
        story.extend(self._bullets(market.get("real_competitors", []), styles["body"]))
        story.append(self._p("Verified sources", styles["h2"]))
        story.extend(self._bullets(market.get("verified_sources", []), styles["small"]))

        story.append(PageBreak())
        story.append(self._p("3. SWOT & Risk Analysis", styles["h1"]))
        s = swot.get("swot") or {}
        swot_rows = [["Strengths", "Weaknesses"], ["\n".join(f"• {x}" for x in s.get("strengths", [])) or "Not provided", "\n".join(f"• {x}" for x in s.get("weaknesses", [])) or "Not provided"],
                     ["Opportunities", "Threats"], ["\n".join(f"• {x}" for x in s.get("opportunities", [])) or "Not provided", "\n".join(f"• {x}" for x in s.get("threats", [])) or "Not provided"]]
        t = Table([[self._p(c, styles["h2"]) if isinstance(c, str) else c for c in row] for row in swot_rows], colWidths=[85*mm,85*mm])
        t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.lightgrey),("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),("BACKGROUND",(0,2),(-1,2),colors.whitesmoke)]))
        story.append(t)
        story.append(self._p("Risk assessment", styles["h2"]))
        risks = swot.get("risk_analysis") or {}
        for label, key in (("High", "high_risks"), ("Medium", "medium_risks"), ("Low", "low_risks")):
            story.append(self._p(f"{label} risks", styles["h2"]))
            for item in risks.get(key, []):
                story.append(self._p(f"{item.get('risk', 'Risk')}: {item.get('description', '')} Mitigation: {item.get('mitigation', '')}", styles["body"]))
        story.append(self._p(f"Competitor risk: {swot.get('competitor_risk', {})}", styles["small"]))
        story.append(self._p(f"Market demand prediction: {swot.get('market_demand_prediction', {})}", styles["small"]))

        story.append(self._p("4. MVP / MoSCoW Recommendation", styles["h1"]))
        m = mvp.get("moscow_framework") or {}
        for label, key in (("Must Have", "must_have"), ("Should Have", "should_have"), ("Could Have", "could_have"), ("Won't Have", "wont_have")):
            story.append(self._p(label, styles["h2"]))
            for item in m.get(key, []):
                story.append(self._p(f"{item.get('feature', 'Feature')}: {item.get('reason', '')} | Effort: {item.get('effort', 'n/a')} | Impact: {item.get('impact', 'n/a')}", styles["body"]))
        story.append(self._p(f"Tech stack: {mvp.get('tech_stack_recommendation', {})}", styles["small"]))
        story.append(self._p(f"Timeline: {mvp.get('mvp_timeline', {})}", styles["small"]))
        story.append(self._p(f"Resources: {mvp.get('resource_requirements', {})}", styles["small"]))
        story.append(self._p(f"Success metrics: {mvp.get('success_metrics', [])}", styles["body"]))

        story.append(PageBreak())
        story.append(self._p("5. Go-To-Market Strategy", styles["h1"]))
        pos = gtm.get("positioning") or {}
        for key in ("value_proposition", "target_segment", "unique_differentiator", "positioning_statement"):
            story.append(self._p(f"{key.replace('_',' ').title()}: {pos.get(key, 'Not provided')}", styles["body"]))
        channels = gtm.get("channels") or {}
        story.append(self._p("Primary channels", styles["h2"]))
        for x in channels.get("primary", []): story.append(self._p(f"{x.get('channel')}: {x.get('strategy')} | Cost: {x.get('cost')}", styles["body"]))
        story.append(self._p("Secondary channels", styles["h2"]))
        for x in channels.get("secondary", []): story.append(self._p(f"{x.get('channel')}: {x.get('strategy')} | Cost: {x.get('cost')}", styles["body"]))
        acq = gtm.get("customer_acquisition") or {}
        for key in ("first_100_customers", "first_1000_customers", "customer_acquisition_cost", "lifetime_value_estimate"):
            story.append(self._p(f"{key.replace('_',' ').title()}: {acq.get(key, 'Not provided')}", styles["body"]))
        story.append(self._p(f"Pricing: {gtm.get('pricing_strategy', {})}", styles["small"]))
        story.append(self._p(f"Launch plan: {gtm.get('launch_plan', {})}", styles["small"]))
        story.append(self._p(f"Growth metrics: {gtm.get('growth_metrics', {})}", styles["small"]))
        story.append(self._p(f"Partnerships: {gtm.get('key_partnerships', [])}", styles["body"]))

        story.append(self._p("6. Conversational Advisor", styles["h1"]))
        story.append(self._p("The validation outputs are ingested into the session knowledge base for follow-up questions across SWOT, MVP and GTM.", styles["body"]))
        story.append(self._p("7. Limitations & Interpretation", styles["h1"]))
        story.append(self._p("Market facts should be checked against the cited live sources. LLM-generated strategy, demand predictions and risk estimates are decision-support outputs, not guarantees.", styles["body"]))

        doc.build(story)
        return str(path)


def generate_validation_report(validation: dict[str, Any]) -> str:
    return StartupValidationReportAgent().generate(validation)
