"""Mock airline, airport, and generated flight catalogue.

All data is fictional sample inventory. It is generated deterministically
from the search inputs so tests stay stable without calling live APIs.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

AIRLINES = [
    {"code": "AI", "name": "Air India", "color": "#C8102E"},
    {"code": "6E", "name": "IndiGo", "color": "#001B94"},
    {"code": "UK", "name": "Vistara", "color": "#4B0082"},
    {"code": "QP", "name": "Akasa Air", "color": "#FF6A00"},
    {"code": "EK", "name": "Emirates", "color": "#D71A21"},
    {"code": "QR", "name": "Qatar Airways", "color": "#5C0632"},
    {"code": "SQ", "name": "Singapore Airlines", "color": "#F9B000"},
]

AIRPORTS = [
    {"code": "DEL", "city": "Delhi", "name": "Indira Gandhi International", "country": "India"},
    {"code": "BOM", "city": "Mumbai", "name": "Chhatrapati Shivaji Maharaj International", "country": "India"},
    {"code": "BLR", "city": "Bengaluru", "name": "Kempegowda International", "country": "India"},
    {"code": "HYD", "city": "Hyderabad", "name": "Rajiv Gandhi International", "country": "India"},
    {"code": "MAA", "city": "Chennai", "name": "Chennai International", "country": "India"},
    {"code": "CCU", "city": "Kolkata", "name": "Netaji Subhas Chandra Bose International", "country": "India"},
    {"code": "COK", "city": "Kochi", "name": "Cochin International", "country": "India"},
    {"code": "AMD", "city": "Ahmedabad", "name": "Sardar Vallabhbhai Patel International", "country": "India"},
    {"code": "GOI", "city": "Goa", "name": "Manohar International", "country": "India"},
    {"code": "JAI", "city": "Jaipur", "name": "Jaipur International", "country": "India"},
    {"code": "PNQ", "city": "Pune", "name": "Pune International", "country": "India"},
    {"code": "IXC", "city": "Chandigarh", "name": "Chandigarh International", "country": "India"},
    {"code": "DXB", "city": "Dubai", "name": "Dubai International", "country": "UAE"},
    {"code": "DOH", "city": "Doha", "name": "Hamad International", "country": "Qatar"},
    {"code": "SIN", "city": "Singapore", "name": "Changi", "country": "Singapore"},
    {"code": "LHR", "city": "London", "name": "Heathrow", "country": "United Kingdom"},
    {"code": "BKK", "city": "Bangkok", "name": "Suvarnabhumi", "country": "Thailand"},
    {"code": "SIN", "city": "Singapore", "name": "Changi", "country": "Singapore"},
]

# Keep unique airport codes
_SEEN = set()
_UNIQUE_AIRPORTS = []
for _airport in AIRPORTS:
    if _airport["code"] not in _SEEN:
        _SEEN.add(_airport["code"])
        _UNIQUE_AIRPORTS.append(_airport)
AIRPORTS = _UNIQUE_AIRPORTS

AIRPORT_INDEX = {a["code"]: a for a in AIRPORTS}

CABIN_CLASSES = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]

CABIN_MULTIPLIER = {
    "ECONOMY": 1.0,
    "PREMIUM_ECONOMY": 1.55,
    "BUSINESS": 3.1,
    "FIRST": 5.4,
}

# Typical block times in minutes for popular pairs (undirected lookup).
ROUTE_MINUTES = {
    frozenset({"DEL", "BOM"}): 130,
    frozenset({"DEL", "BLR"}): 160,
    frozenset({"DEL", "HYD"}): 140,
    frozenset({"DEL", "MAA"}): 165,
    frozenset({"DEL", "CCU"}): 130,
    frozenset({"DEL", "GOI"}): 155,
    frozenset({"DEL", "COK"}): 195,
    frozenset({"DEL", "AMD"}): 90,
    frozenset({"DEL", "JAI"}): 70,
    frozenset({"DEL", "PNQ"}): 125,
    frozenset({"BOM", "BLR"}): 100,
    frozenset({"BOM", "HYD"}): 85,
    frozenset({"BOM", "MAA"}): 110,
    frozenset({"BOM", "GOI"}): 70,
    frozenset({"BOM", "COK"}): 115,
    frozenset({"BOM", "CCU"}): 155,
    frozenset({"BLR", "HYD"}): 70,
    frozenset({"BLR", "MAA"}): 65,
    frozenset({"BLR", "GOI"}): 75,
    frozenset({"DEL", "DXB"}): 215,
    frozenset({"BOM", "DXB"}): 190,
    frozenset({"DEL", "DOH"}): 230,
    frozenset({"BOM", "DOH"}): 205,
    frozenset({"DEL", "SIN"}): 330,
    frozenset({"BOM", "SIN"}): 315,
    frozenset({"BLR", "SIN"}): 270,
    frozenset({"DEL", "LHR"}): 540,
    frozenset({"BOM", "LHR"}): 555,
    frozenset({"DEL", "BKK"}): 240,
    frozenset({"BOM", "BKK"}): 255,
}


def _stable_int(seed: str, modulo: int) -> int:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % modulo


def _block_minutes(origin: str, destination: str) -> int:
    key = frozenset({origin, destination})
    if key in ROUTE_MINUTES:
        return ROUTE_MINUTES[key]
    origin_intl = AIRPORT_INDEX[origin]["country"] != "India"
    dest_intl = AIRPORT_INDEX[destination]["country"] != "India"
    if origin_intl or dest_intl:
        return 280 + _stable_int(f"{origin}{destination}", 260)
    return 80 + _stable_int(f"{origin}{destination}", 90)


def _base_price(origin: str, destination: str, minutes: int) -> int:
    intl = AIRPORT_INDEX[origin]["country"] != AIRPORT_INDEX[destination]["country"]
    floor = 18500 if intl else 3200
    return floor + minutes * (42 if intl else 18)


def _format_duration(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def _departure_bucket(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def generate_flights(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str,
    passengers: int,
) -> list[dict[str, Any]]:
    """Create a deterministic set of mock flights for a city pair and date."""
    cabin_class = cabin_class.upper()
    block = _block_minutes(origin, destination)
    origin_meta = AIRPORT_INDEX[origin]
    dest_meta = AIRPORT_INDEX[destination]
    day = datetime.strptime(departure_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    flights: list[dict[str, Any]] = []

    templates = [
        ("AI", 0, 6, 25, 0, 1.00),
        ("6E", 1, 7, 40, 0, 0.82),
        ("UK", 2, 9, 10, 0, 1.12),
        ("QP", 3, 11, 5, 0, 0.88),
        ("6E", 4, 14, 20, 0, 0.79),
        ("AI", 5, 16, 45, 1, 0.91),
        ("UK", 6, 18, 55, 0, 1.18),
        ("EK", 7, 2, 15, 1, 1.65),
        ("QR", 8, 3, 40, 1, 1.58),
        ("SQ", 9, 22, 10, 1, 1.72),
        ("AI", 10, 20, 30, 0, 1.05),
        ("6E", 11, 13, 5, 1, 0.74),
    ]

    intl = origin_meta["country"] != dest_meta["country"]
    for airline_code, idx, hour, minute, stops, price_factor in templates:
        airline = next(a for a in AIRLINES if a["code"] == airline_code)
        # Keep long-haul carriers off short domestic hops, and vice versa.
        long_haul = airline_code in {"EK", "QR", "SQ"}
        if long_haul and not intl and block < 180:
            continue
        if not long_haul and intl and block > 360 and idx % 3 != 0:
            continue

        extra = 0 if stops == 0 else 55 + (stops * 40)
        duration_min = block + extra + _stable_int(f"{origin}{destination}{idx}", 18)
        depart = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
        arrive = depart + timedelta(minutes=duration_min)
        price = int(
            _base_price(origin, destination, duration_min)
            * price_factor
            * CABIN_MULTIPLIER[cabin_class]
        )
        # Round to a fare-looking number
        price = (price // 50) * 50 + 49 if price % 10 != 9 else price
        seats = 4 + _stable_int(f"{departure_date}{airline_code}{idx}{origin}", 28)
        flight_number = f"{airline_code}{120 + _stable_int(origin + destination + str(idx), 780)}"
        flight_id = (
            f"{airline_code}-{origin}-{destination}-{departure_date.replace('-', '')}-{idx:02d}"
        )

        flights.append(
            {
                "flightId": flight_id,
                "airline": airline["name"],
                "airlineCode": airline["code"],
                "airlineColor": airline["color"],
                "flightNumber": flight_number,
                "origin": origin,
                "originCity": origin_meta["city"],
                "originAirport": origin_meta["name"],
                "destination": destination,
                "destinationCity": dest_meta["city"],
                "destinationAirport": dest_meta["name"],
                "departureTime": depart.isoformat(),
                "arrivalTime": arrive.isoformat(),
                "durationMinutes": duration_min,
                "duration": _format_duration(duration_min),
                "stops": stops,
                "stopLabel": "Non-stop" if stops == 0 else f"{stops} stop" if stops == 1 else f"{stops} stops",
                "price": price,
                "currency": "INR",
                "cabinClass": cabin_class,
                "availableSeats": seats,
                "departureBucket": _departure_bucket(hour),
                "arrivalBucket": _departure_bucket(arrive.hour),
                "passengersRequested": passengers,
            }
        )

    return flights


def get_flight_by_id(flight_id: str) -> dict[str, Any] | None:
    """Rehydrate a generated flight from its deterministic id."""
    try:
        airline_code, origin, destination, ymd, idx_s = flight_id.split("-")
        departure_date = f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}"
        idx = int(idx_s)
    except (ValueError, IndexError):
        return None
    if origin not in AIRPORT_INDEX or destination not in AIRPORT_INDEX:
        return None
    # Generate across cabin classes and pick the matching id
    for cabin in CABIN_CLASSES:
        for flight in generate_flights(origin, destination, departure_date, cabin, 1):
            if flight["flightId"] == flight_id and flight["airlineCode"] == airline_code:
                # idx is encoded in the id; cabin isn't, so return ECONOMY by default
                # unless a later search specified otherwise. Details endpoint uses ECONOMY fares
                # unless cabinClass is supplied by the caller.
                _ = idx
                return flight
    return None
