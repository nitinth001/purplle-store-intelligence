# PROMPT:
# Generate pytest tests for a FastAPI Store Intelligence API that validates health,
# metrics, event ingestion, and edge-case stability.
#
# CHANGES MADE:
# Simplified tests for MVP validation, added schema checks, and avoided dependence
# on raw CCTV files so tests can run quickly in CI or reviewer machines.

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_metrics_endpoint():
    response = client.get("/stores/STORE_PURPLLE_001/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "store_id" in data
    assert "unique_visitors" in data
    assert "conversion_rate" in data


def test_heatmap_endpoint():
    response = client.get("/stores/STORE_PURPLLE_001/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "heatmap" in data


def test_empty_ingest_batch():
    response = client.post("/events/ingest", json={"events": []})
    assert response.status_code == 200