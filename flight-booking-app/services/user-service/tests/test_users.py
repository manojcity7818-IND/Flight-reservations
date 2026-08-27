from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "UP", "service": "user"}


def test_create_and_retrieve_user():
    created = client.post(
        "/api/users",
        json={"firstName": "Rahul", "lastName": "Singh", "email": "rahul@example.com", "phone": "9988776655"},
    )
    assert created.status_code == 201
    user_id = created.json()["userId"]
    fetched = client.get(f"/api/users/{user_id}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "rahul@example.com"


def test_invalid_user_not_found():
    assert client.get("/api/users/USMISSING").status_code == 404


def test_invalid_phone():
    response = client.post(
        "/api/users",
        json={"firstName": "A", "lastName": "B", "email": "ab@example.com", "phone": "not-a-phone"},
    )
    assert response.status_code == 400


def test_invalid_email():
    response = client.post(
        "/api/users",
        json={"firstName": "A", "lastName": "B", "email": "bad", "phone": "9988776655"},
    )
    assert response.status_code == 422
