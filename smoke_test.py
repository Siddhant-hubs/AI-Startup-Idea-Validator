"""Local smoke tests that do not call paid/live LLM APIs."""

from web_search_agent import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["milestone"] == "4"

if __name__ == "__main__":
    test_health()
    print("Smoke test passed: /health")
