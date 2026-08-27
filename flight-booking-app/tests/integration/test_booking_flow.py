import httpx


def test_health_via_gateway(stack):
    response = httpx.get(f"{stack}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_end_to_end_booking_flow(stack):
    client = httpx.Client(base_url=stack, timeout=10)

    search = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "cabinClass": "ECONOMY"},
    )
    assert search.status_code == 200
    flight = search.json()["outbound"][0]

    user = client.post(
        "/api/users",
        json={"firstName": "Neha", "lastName": "Kapoor", "email": "neha@example.com", "phone": "9123456780"},
    )
    assert user.status_code == 201

    booking = client.post(
        "/api/bookings",
        json={
            "flightId": flight["flightId"],
            "outboundFlight": {
                "flightId": flight["flightId"],
                "airline": flight["airline"],
                "flightNumber": flight["flightNumber"],
                "origin": flight["origin"],
                "destination": flight["destination"],
                "departureTime": flight["departureTime"],
                "arrivalTime": flight["arrivalTime"],
                "cabinClass": flight["cabinClass"],
                "duration": flight["duration"],
                "stops": flight["stops"],
            },
            "passengers": [{"firstName": "Neha", "lastName": "Kapoor", "type": "ADULT"}],
            "contact": {"email": "neha@example.com", "phone": "9123456780"},
            "totalPrice": flight["price"],
            "currency": "INR",
            "userId": user.json()["userId"],
        },
    )
    assert booking.status_code == 201
    booking_id = booking.json()["bookingId"]
    assert booking.json()["bookingStatus"] == "PENDING"

    failed = client.post(
        "/api/payments",
        json={"bookingId": booking_id, "amount": flight["price"], "currency": "INR", "simulateOutcome": "FAILED"},
    )
    assert failed.json()["status"] == "FAILED"

    paid = client.post(
        "/api/payments",
        json={"bookingId": booking_id, "amount": flight["price"], "currency": "INR", "simulateOutcome": "SUCCESS"},
    )
    assert paid.json()["status"] == "SUCCESS"

    confirmed = client.post(
        f"/api/bookings/{booking_id}/confirm",
        json={"paymentStatus": "SUCCESS", "paymentId": paid.json()["paymentId"]},
    )
    assert confirmed.json()["bookingStatus"] == "CONFIRMED"

    note = client.post(
        "/api/notifications",
        json={"bookingId": booking_id, "type": "BOOKING_CONFIRMATION", "recipient": "neha@example.com"},
    )
    assert note.json()["status"] == "SENT"

    fetched = client.get(f"/api/bookings/{booking_id}")
    assert fetched.json()["bookingStatus"] == "CONFIRMED"
    assert fetched.json()["paymentStatus"] == "SUCCESS"
