"""Unit tests for the Flask demo service."""

import pytest
from app.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_index_returns_running_status(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "running"
    assert "version" in body


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "healthy"
    assert "uptime_seconds" in body


def test_api_data_returns_case_studies(client):
    response = client.get("/api/data")
    assert response.status_code == 200
    body = response.get_json()
    names = [item["name"] for item in body["data"]]
    assert names == ["Netflix", "Amazon", "Capital One"]


def test_error_endpoint_increments_status(client):
    response = client.get("/api/error")
    assert response.status_code == 500
    assert "error" in response.get_json()


def test_metrics_exposes_prometheus_text(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text
