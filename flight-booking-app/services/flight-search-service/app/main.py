from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.data import (
    AIRPORT_INDEX,
    AIRPORTS,
    CABIN_CLASSES,
    generate_flights,
    get_flight_by_id,
)

app = FastAPI(title="My Booking Flight Search", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SortOption = Literal["cheapest", "fastest", "best", "earliest"]


@app.get("/health")
def health():
    return {"status": "UP", "service": "flight-search"}


@app.get("/api/airports")
def list_airports(q: str | None = None):
    query = (q or "").strip().lower()
    if not query:
        return {"airports": AIRPORTS}
    matches = [
        a
        for a in AIRPORTS
        if query in a["code"].lower()
        or query in a["city"].lower()
        or query in a["name"].lower()
    ]
    return {"airports": matches}


def _validate_search(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None,
    cabin_class: str,
    passengers: int,
):
    origin = origin.upper()
    destination = destination.upper()
    if origin not in AIRPORT_INDEX:
        raise HTTPException(status_code=400, detail="Invalid origin airport. Choose a supported city or airport code.")
    if destination not in AIRPORT_INDEX:
        raise HTTPException(status_code=400, detail="Invalid destination airport. Choose a supported city or airport code.")
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination must be different.")
    try:
        dep = date.fromisoformat(departure_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Departure date must be in YYYY-MM-DD format.") from exc
    ret = None
    if return_date:
        try:
            ret = date.fromisoformat(return_date)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Return date must be in YYYY-MM-DD format.") from exc
        if ret < dep:
            raise HTTPException(status_code=400, detail="Return date cannot be before the departure date.")
    cabin = cabin_class.upper()
    if cabin not in CABIN_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid cabin class.")
    if passengers < 1 or passengers > 9:
        raise HTTPException(status_code=400, detail="Passengers must be between 1 and 9.")
    return origin, destination, cabin


def _apply_filters(
    flights: list[dict],
    min_price: int | None,
    max_price: int | None,
    airlines: str | None,
    stops: str | None,
    departure_time: str | None,
    arrival_time: str | None,
    max_duration: int | None,
    cabin_class: str | None,
):
    results = flights
    if min_price is not None:
        results = [f for f in results if f["price"] >= min_price]
    if max_price is not None:
        results = [f for f in results if f["price"] <= max_price]
    if airlines:
        codes = {c.strip().upper() for c in airlines.split(",") if c.strip()}
        results = [f for f in results if f["airlineCode"] in codes]
    if stops is not None and stops != "":
        allowed = {int(s.strip()) for s in stops.split(",") if s.strip() != ""}
        results = [f for f in results if f["stops"] in allowed]
    if departure_time:
        buckets = {b.strip().lower() for b in departure_time.split(",") if b.strip()}
        results = [f for f in results if f["departureBucket"] in buckets]
    if arrival_time:
        buckets = {b.strip().lower() for b in arrival_time.split(",") if b.strip()}
        results = [f for f in results if f["arrivalBucket"] in buckets]
    if max_duration is not None:
        results = [f for f in results if f["durationMinutes"] <= max_duration]
    if cabin_class:
        results = [f for f in results if f["cabinClass"] == cabin_class.upper()]
    return results


def _sort_flights(flights: list[dict], sort: SortOption) -> list[dict]:
    if sort == "cheapest":
        return sorted(flights, key=lambda f: (f["price"], f["durationMinutes"]))
    if sort == "fastest":
        return sorted(flights, key=lambda f: (f["durationMinutes"], f["price"]))
    if sort == "earliest":
        return sorted(flights, key=lambda f: (f["departureTime"], f["price"]))
    # best: blend of price, duration, and fewer stops
    return sorted(
        flights,
        key=lambda f: (f["stops"], f["price"] * 0.6 + f["durationMinutes"] * 18, f["departureTime"]),
    )


@app.get("/api/flights")
def search_flights(
    origin: str | None = Query(None, alias="from"),
    destination: str | None = Query(None, alias="to"),
    departureDate: str | None = None,
    returnDate: str | None = None,
    passengers: int = 1,
    cabinClass: str = "ECONOMY",
    minPrice: int | None = None,
    maxPrice: int | None = None,
    airlines: str | None = None,
    stops: str | None = None,
    departureTime: str | None = None,
    arrivalTime: str | None = None,
    maxDuration: int | None = None,
    sort: SortOption = "best",
):
    if not origin or not destination or not departureDate:
        raise HTTPException(
            status_code=400,
            detail="from, to, and departureDate are required.",
        )
    origin, destination, cabin = _validate_search(
        origin, destination, departureDate, returnDate, cabinClass, passengers
    )

    outbound = generate_flights(origin, destination, departureDate, cabin, passengers)
    outbound = [f for f in outbound if f["availableSeats"] >= passengers]
    outbound = _apply_filters(
        outbound, minPrice, maxPrice, airlines, stops, departureTime, arrivalTime, maxDuration, cabin
    )
    outbound = _sort_flights(outbound, sort)

    inbound = []
    if returnDate:
        inbound = generate_flights(destination, origin, returnDate, cabin, passengers)
        inbound = [f for f in inbound if f["availableSeats"] >= passengers]
        inbound = _apply_filters(
            inbound, minPrice, maxPrice, airlines, stops, departureTime, arrivalTime, maxDuration, cabin
        )
        inbound = _sort_flights(inbound, sort)

    return {
        "tripType": "ROUND_TRIP" if returnDate else "ONE_WAY",
        "from": origin,
        "to": destination,
        "departureDate": departureDate,
        "returnDate": returnDate,
        "passengers": passengers,
        "cabinClass": cabin,
        "currency": "INR",
        "outbound": outbound,
        "inbound": inbound,
        "count": len(outbound) + len(inbound),
    }


@app.get("/api/flights/{flight_id}")
def flight_details(flight_id: str, cabinClass: str = "ECONOMY"):
    flight = get_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found.")
    # Re-generate at requested cabin for accurate fare
    regenerated = generate_flights(
        flight["origin"],
        flight["destination"],
        datetime.fromisoformat(flight["departureTime"]).date().isoformat(),
        cabinClass.upper(),
        1,
    )
    match = next((f for f in regenerated if f["flightId"] == flight_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Flight not found.")
    return match
