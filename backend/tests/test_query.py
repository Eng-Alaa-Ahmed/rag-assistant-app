from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("app.api.routes.query.generation.generate_answer", return_value="A resistor limits current. (Source 1, Page 174)")
@patch(
    "app.api.routes.query.retrieval.retrieve",
    return_value=[{"text": "A resistor limits current flow.", "page_number": 174, "distance": 0.4}],
)
def test_query_happy_path(mock_retrieve, mock_generate):
    response = client.post("/query", json={"question": "What is a resistor?"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "sources" in body
    assert body["sources"] == ["Page 174"]


def test_query_invalid_input():
    response = client.post("/query", json={})
    assert response.status_code == 422