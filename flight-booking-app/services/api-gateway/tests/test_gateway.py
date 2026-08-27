from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "UP", "service": "api-gateway"}


def test_unknown_prefix():
    response = client.get("/api/unknown")
    assert response.status_code == 404
