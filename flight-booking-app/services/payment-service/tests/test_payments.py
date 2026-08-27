from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "UP", "service": "payment"}


def test_successful_payment():
    response = client.post(
        "/api/payments",
        json={"bookingId": "BK12345", "amount": 6450, "currency": "INR", "simulateOutcome": "SUCCESS"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["paymentId"].startswith("PAY")
    fetched = client.get(f"/api/payments/{data['paymentId']}")
    assert fetched.json()["status"] == "SUCCESS"


def test_failed_payment():
    response = client.post(
        "/api/payments",
        json={"bookingId": "BK12345", "amount": 6450, "currency": "INR", "simulateOutcome": "FAILED"},
    )
    assert response.json()["status"] == "FAILED"


def test_failed_demo_instrument():
    response = client.post(
        "/api/payments",
        json={
            "bookingId": "BK12345",
            "amount": 6450,
            "currency": "INR",
            "demoInstrument": "demo-0000",
        },
    )
    assert response.json()["status"] == "FAILED"


def test_invalid_payment_amount():
    response = client.post(
        "/api/payments",
        json={"bookingId": "BK12345", "amount": 0, "currency": "INR"},
    )
    assert response.status_code == 422


def test_payment_not_found():
    assert client.get("/api/payments/PAYMISSING").status_code == 404
