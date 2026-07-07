import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_providers_endpoint():
    r = client.get("/api/providers")
    assert r.status_code == 200
    names = {p["name"] for p in r.json()}
    assert "mock" in names and "gemini" in names


def test_iterate_with_mock():
    r = client.post(
        "/api/iterate",
        json={"task": "compute the average of a list", "provider": "mock", "max_iterations": 2},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["final_solution"]
    assert data["steps"][0]["role"] == "generator"


def test_iterate_validates_task():
    r = client.post("/api/iterate", json={"task": "", "provider": "mock"})
    assert r.status_code == 422


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "IteraMind" in r.text


def test_stream_endpoint():
    r = client.post(
        "/api/iterate/stream",
        json={"task": "hello world", "provider": "mock", "max_iterations": 2},
    )
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert '"type": "done"' in r.text
