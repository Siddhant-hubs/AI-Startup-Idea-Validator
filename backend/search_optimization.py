"""Milestone 4 search-query optimization utilities.

Keeps query construction deterministic, focused, and easy to test.
"""

import re

STOPWORDS = {"a", "an", "the", "for", "and", "or", "of", "to", "in", "on", "with", "is", "ai"}


def normalize_idea(idea: str) -> str:
    value = re.sub(r"\s+", " ", (idea or "").strip())
    return value[:180]


def build_search_queries(idea: str) -> dict[str, str]:
    """Build intent-specific queries instead of one generic query."""
    idea = normalize_idea(idea)
    return {
        "industry": f'"{idea}" industry trends market demand recent news',
        "market": f'"{idea}" market size revenue CAGR growth statistics 2025 2026',
        "competitors": f'"{idea}" competitors alternatives startups products',
        "customers": f'"{idea}" target customers pain points adoption use cases',
    }


def query_quality_score(query: str) -> float:
    """Simple deterministic query-quality heuristic for Milestone 4 testing."""
    q = (query or "").strip()
    if not q:
        return 0.0
    words = q.split()
    score = 0.4
    if len(words) >= 5:
        score += 0.2
    if any(k in q.lower() for k in ("market", "competitors", "trends", "customers")):
        score += 0.2
    if '"' in q:
        score += 0.1
    if len(q) <= 180:
        score += 0.1
    return min(score, 1.0)
