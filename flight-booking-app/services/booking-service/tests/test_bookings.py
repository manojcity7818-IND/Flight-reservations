from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FLIGHT = {
    "flightId": "AI-DEL-BOM-20260910-00",
    "airline": "Air India",
    "flightNumber": "AI131",
    "origin": "DEL",
    "destination": "BOM",
    "departureTime": "2026-09-10T06:25:00+00:00",
    "arrivalTime": "2026-09-10T08:35:00+00:00",
    "cabinClass": "ECONOMY",
    "duration": "2h 10m",
    "stops": 0,
}


def _payload(**overrides):
    body = {
        "flightId": FLIGHT["flightId"],
        "outboundFlight": FLIGHT,
        "passengers": [{"firstName": "Asha", "lastName": "Mehta", "type": "ADULT"}],
        "contact": {"email": "asha@example.com", "phone": "9876543210"},
        "totalPrice": 6450,
        "currency": "INR",
    }
    body.update(overrides)
    return body


def test_health():
    response = client.get("/health")
    assert response.json() == {"status": "UP", "service": "booking"}


def test_create_and_retrieve_booking():
    created = client.post("/api/bookings", json=_payload())
    assert created.status_code == 201
    data = created.json()
    assert data["bookingStatus"] == "PENDING"
    assert data["paymentStatus"] == "UNPAID"
    booking_id = data["bookingId"]
    fetched = client.get(f"/api/bookings/{booking_id}")
    assert fetched.status_code == 200
    assert fetched.json()["bookingId"] == booking_id


def test_confirm_booking():
    booking_id = client.post("/api/bookings", json=_payload()).json()["bookingId"]
    confirmed = client.post(
        f"/api/bookings/{booking_id}/confirm",
        json={"paymentStatus": "SUCCESS", "paymentId": "PAYTEST"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["bookingStatus"] == "CONFIRMED"
    assert confirmed.json()["paymentStatus"] == "SUCCESS"


def test_cancel_booking():
    booking_id = client.post("/api/bookings", json=_payload()).json()["bookingId"]
    cancelled = client.post(f"/api/bookings/{booking_id}/cancel")
    assert cancelled.json()["bookingStatus"] == "CANCELLED"


def test_invalid_booking_not_found():
    response = client.get("/api/bookings/BKDOESNOTEXIST")
    assert response.status_code == 404


def test_invalid_passenger_rejected():
    response = client.post("/api/bookings", json=_payload(passengers=[]))
    assert response.status_code == 422


def test_mismatched_flight_id():
    response = client.post("/api/bookings", json=_payload(flightId="OTHER"))
    assert response.status_code == 400


def test_cannot_confirm_cancelled():
    booking_id = client.post("/api/bookings", json=_payload()).json()["bookingId"]
    client.post(f"/api/bookings/{booking_id}/cancel")
    response = client.post(f"/api/bookings/{booking_id}/confirm")
    assert response.status_code == 400
