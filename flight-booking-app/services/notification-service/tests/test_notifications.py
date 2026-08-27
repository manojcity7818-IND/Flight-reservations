from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "UP", "service": "notification"}


def test_booking_notification():
    response = client.post(
        "/api/notifications",
        json={"bookingId": "BK12345", "type": "BOOKING_CONFIRMATION", "recipient": "user@example.com"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "SENT"
    assert response.json()["type"] == "BOOKING_CONFIRMATION"


def test_payment_notification():
    response = client.post(
        "/api/notifications",
        json={"bookingId": "BK12345", "type": "PAYMENT_CONFIRMATION", "recipient": "user@example.com"},
    )
    assert response.json()["status"] == "SENT"
    assert "Payment" in response.json()["message"]


def test_cancellation_notification():
    response = client.post(
        "/api/notifications",
        json={"bookingId": "BK12345", "type": "CANCELLATION", "recipient": "user@example.com"},
    )
    assert response.json()["type"] == "CANCELLATION"


def test_list_by_booking():
    client.post(
        "/api/notifications",
        json={"bookingId": "BK999", "type": "BOOKING_CONFIRMATION", "recipient": "a@example.com"},
    )
    listed = client.get("/api/notifications", params={"bookingId": "BK999"})
    assert listed.status_code == 200
    assert listed.json()["notifications"]
