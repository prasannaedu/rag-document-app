import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


def test_rag_status():
    response = client.get("/rag/status")
    assert response.status_code == 200
    assert "embeddings_initialized" in response.json()


@patch("app.dependencies.get_current_user")
def test_rag_query_valid(mock_user_dep):
    mock_user_dep.return_value = {"id": 1, "username": "testuser", "is_admin": True}
    payload = {"query": "What is Python?"}
    response = client.post("/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


@patch("app.dependencies.get_current_user")
def test_rag_query_empty(mock_user_dep):
    mock_user_dep.return_value = {"id": 1, "username": "testuser", "is_admin": True}
    payload = {"query": ""}
    response = client.post("/rag/query", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Query string is required."


@patch("app.dependencies.get_current_user")
def test_rag_reindex_as_admin(mock_user_dep):
    mock_user_dep.return_value = {"id": 1, "username": "admin", "is_admin": True}
    response = client.post("/rag/reindex")
    assert response.status_code == 200
    assert response.json()["detail"] == "Reindexing started."


@patch("app.dependencies.get_current_user")
def test_rag_reindex_not_admin(mock_user_dep):
    mock_user_dep.return_value = {"id": 2, "username": "normal", "is_admin": False}
    response = client.post("/rag/reindex")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required."
