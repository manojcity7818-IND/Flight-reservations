from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_flights_delhi_mumbai():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "passengers": 1, "cabinClass": "ECONOMY"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["from"] == "DEL"
    assert data["to"] == "BOM"
    assert data["count"] > 0
    flight = data["outbound"][0]
    for key in (
        "flightId",
        "airline",
        "flightNumber",
        "origin",
        "destination",
        "departureTime",
        "arrivalTime",
        "duration",
        "stops",
        "price",
        "currency",
        "cabinClass",
        "availableSeats",
    ):
        assert key in flight


def test_round_trip_returns_inbound():
    response = client.get(
        "/api/flights",
        params={
            "from": "DEL",
            "to": "BOM",
            "departureDate": "2026-09-10",
            "returnDate": "2026-09-18",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tripType"] == "ROUND_TRIP"
    assert data["inbound"]
    assert data["inbound"][0]["origin"] == "BOM"


def test_filter_nonstop():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "stops": "0"},
    )
    assert response.status_code == 200
    assert all(f["stops"] == 0 for f in response.json()["outbound"])


def test_filter_airline():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "airlines": "AI,6E"},
    )
    assert response.status_code == 200
    assert all(f["airlineCode"] in {"AI", "6E"} for f in response.json()["outbound"])


def test_sort_cheapest():
    response = client.get(
        "/api/flights",
        params={"from": "BLR", "to": "HYD", "departureDate": "2026-10-01", "sort": "cheapest"},
    )
    prices = [f["price"] for f in response.json()["outbound"]]
    assert prices == sorted(prices)


def test_sort_fastest():
    response = client.get(
        "/api/flights",
        params={"from": "BLR", "to": "HYD", "departureDate": "2026-10-01", "sort": "fastest"},
    )
    durations = [f["durationMinutes"] for f in response.json()["outbound"]]
    assert durations == sorted(durations)


def test_sort_earliest():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "GOI", "departureDate": "2026-11-02", "sort": "earliest"},
    )
    times = [f["departureTime"] for f in response.json()["outbound"]]
    assert times == sorted(times)


def test_same_origin_destination():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "DEL", "departureDate": "2026-09-10"},
    )
    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()


def test_invalid_origin():
    response = client.get(
        "/api/flights",
        params={"from": "XXX", "to": "BOM", "departureDate": "2026-09-10"},
    )
    assert response.status_code == 400


def test_invalid_destination():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "ZZZ", "departureDate": "2026-09-10"},
    )
    assert response.status_code == 400


def test_invalid_date():
    response = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "10-09-2026"},
    )
    assert response.status_code == 400


def test_return_before_departure():
    response = client.get(
        "/api/flights",
        params={
            "from": "DEL",
            "to": "BOM",
            "departureDate": "2026-09-18",
            "returnDate": "2026-09-10",
        },
    )
    assert response.status_code == 400


def test_missing_required_params():
    response = client.get("/api/flights")
    assert response.status_code == 400


def test_no_flights_for_tight_filters():
    response = client.get(
        "/api/flights",
        params={
            "from": "DEL",
            "to": "BOM",
            "departureDate": "2026-09-10",
            "maxPrice": 1,
        },
    )
    assert response.status_code == 200
    assert response.json()["outbound"] == []
    assert response.json()["count"] == 0


def test_airport_search():
    response = client.get("/api/airports", params={"q": "del"})
    assert response.status_code == 200
    codes = [a["code"] for a in response.json()["airports"]]
    assert "DEL" in codes


def test_flight_details():
    search = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10"},
    )
    flight_id = search.json()["outbound"][0]["flightId"]
    details = client.get(f"/api/flights/{flight_id}")
    assert details.status_code == 200
    assert details.json()["flightId"] == flight_id


def test_business_cabin_is_more_expensive():
    eco = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "cabinClass": "ECONOMY", "sort": "cheapest"},
    )
    biz = client.get(
        "/api/flights",
        params={"from": "DEL", "to": "BOM", "departureDate": "2026-09-10", "cabinClass": "BUSINESS", "sort": "cheapest"},
    )
    assert biz.json()["outbound"][0]["price"] > eco.json()["outbound"][0]["price"]
