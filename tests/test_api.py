"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ask_endpoint():
    """Test ask endpoint."""
    response = client.post("/api/ask", json={"question": "test question"})
    assert response.status_code == 200
    assert "question" in response.json()
    assert "matches" in response.json()


def test_graph_statistics():
    """Test graph statistics endpoint."""
    response = client.get("/api/graph/statistics")
    assert response.status_code == 200
    assert "node_count" in response.json()


def test_settings():
    """Test settings endpoint."""
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert "read_only_mode" in response.json()

