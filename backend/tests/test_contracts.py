"""Milestone 4 — deterministic contract tests.

These tests do not call any external API. They verify the shape and
behaviour of pure, deterministic modules: search query construction
and output-contract quality scoring.
"""

from search_optimization import build_search_queries, normalize_idea, query_quality_score
from quality_checks import score_validation


IDEA = "AI tutor for engineering students"


# ---------------------------------------------------------------------------
# search_optimization
# ---------------------------------------------------------------------------

def test_normalize_idea_trims_and_collapses_whitespace():
    assert normalize_idea("  AI   tutor   for   students  ") == "AI tutor for students"


def test_normalize_idea_truncates_long_input():
    long_idea = "x" * 500
    assert len(normalize_idea(long_idea)) == 180


def test_build_search_queries_has_all_expected_intents():
    queries = build_search_queries(IDEA)
    assert set(queries.keys()) == {"industry", "market", "competitors", "customers"}
    for query in queries.values():
        assert IDEA in query
        assert isinstance(query, str) and len(query) > 0


def test_query_quality_score_rewards_specific_queries():
    good = f'"{IDEA}" market size revenue CAGR growth statistics 2025 2026'
    bad = "idea"
    assert query_quality_score(good) > query_quality_score(bad)


def test_query_quality_score_bounds():
    assert query_quality_score("") == 0.0
    assert 0.0 <= query_quality_score("a normal enough market query with competitors") <= 1.0


# ---------------------------------------------------------------------------
# quality_checks
# ---------------------------------------------------------------------------

def _complete_validation():
    return {
        "market_validation": {
            "market_size": "$1B",
            "real_competitors": ["Competitor A"],
            "confidence_score": 0.8,
            "verified_sources": ["https://example.com"],
        },
        "swot_analysis": {
            "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
            "risk_analysis": {},
        },
        "mvp_features": {
            "moscow_framework": {
                "must_have": [], "should_have": [], "could_have": [], "wont_have": [],
            }
        },
        "gtm_strategy": {
            "positioning": {}, "channels": {}, "customer_acquisition": {},
            "pricing_strategy": {}, "launch_plan": {}, "growth_metrics": {},
        },
    }


def test_score_validation_perfect_payload_scores_100():
    result = score_validation(_complete_validation())
    assert result["passed"] == 4
    assert result["total"] == 4
    assert result["accuracy_score"] == 100.0
    assert result["errors"] == []


def test_score_validation_empty_payload_scores_0_not_negative():
    result = score_validation({})
    assert result["passed"] == 0
    assert result["accuracy_score"] == 0.0
    assert result["accuracy_score"] >= 0.0  # must never go negative
    assert len(result["errors"]) > 0


def test_score_validation_partial_failure_is_proportional():
    data = _complete_validation()
    data["mvp_features"] = {"moscow_framework": {"must_have": "not-a-list"}}
    result = score_validation(data)
    assert result["passed"] == 3
    assert result["accuracy_score"] == 75.0
    assert any("must_have" in e for e in result["errors"])


def test_score_validation_accuracy_score_always_in_valid_range():
    for payload in (_complete_validation(), {}, {"market_validation": {}}):
        result = score_validation(payload)
        assert 0.0 <= result["accuracy_score"] <= 100.0
