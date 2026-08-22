"""Milestone 4 deterministic quality/accuracy checks."""

from typing import Any


def check_market_output(data: dict[str, Any]) -> list[str]:
    required = ["market_size", "real_competitors", "confidence_score", "verified_sources"]
    return [f"Missing market field: {k}" for k in required if k not in data]


def check_swot_output(data: dict[str, Any]) -> list[str]:
    errors=[]
    s=data.get("swot", {})
    for k in ("strengths","weaknesses","opportunities","threats"):
        if not isinstance(s.get(k), list): errors.append(f"SWOT field {k} must be a list")
    if "risk_analysis" not in data: errors.append("Missing risk_analysis")
    return errors


def check_mvp_output(data: dict[str, Any]) -> list[str]:
    errors=[]; m=data.get("moscow_framework", {})
    for k in ("must_have","should_have","could_have","wont_have"):
        if not isinstance(m.get(k), list): errors.append(f"MoSCoW field {k} must be a list")
    return errors


def check_gtm_output(data: dict[str, Any]) -> list[str]:
    errors=[]
    for k in ("positioning","channels","customer_acquisition","pricing_strategy","launch_plan","growth_metrics"):
        if k not in data: errors.append(f"Missing GTM field: {k}")
    return errors


def score_validation(data: dict[str, Any]) -> dict[str, Any]:
    sections = {
        "market_validation": check_market_output(data.get("market_validation", {})),
        "swot_analysis": check_swot_output(data.get("swot_analysis", {})),
        "mvp_features": check_mvp_output(data.get("mvp_features", {})),
        "gtm_strategy": check_gtm_output(data.get("gtm_strategy", {})),
    }
    total = len(sections)
    passed = sum(1 for errors in sections.values() if not errors)
    checks = [err for errors in sections.values() for err in errors]
    return {"passed": passed, "total": total, "accuracy_score": round(passed / total * 100, 1), "errors": checks}
