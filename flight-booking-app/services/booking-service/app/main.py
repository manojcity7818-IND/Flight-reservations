from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="My Booking Flight Bookings", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BookingStatus = Literal["PENDING", "CONFIRMED", "CANCELLED"]
PaymentStatus = Literal["UNPAID", "SUCCESS", "FAILED"]

_STORE: dict[str, dict] = {}
_LOCK = Lock()


class Passenger(BaseModel):
    firstName: str = Field(min_length=1, max_length=60)
    lastName: str = Field(min_length=1, max_length=60)
    dateOfBirth: str | None = None
    type: Literal["ADULT", "CHILD", "INFANT"] = "ADULT"


class Contact(BaseModel):
    email: EmailStr
    phone: str = Field(min_length=8, max_length=20)


class FlightSnapshot(BaseModel):
    flightId: str
    airline: str
    flightNumber: str
    origin: str
    destination: str
    departureTime: str
    arrivalTime: str
    cabinClass: str
    duration: str | None = None
    stops: int = 0


class CreateBookingRequest(BaseModel):
    flightId: str = Field(min_length=3)
    outboundFlight: FlightSnapshot
    inboundFlight: FlightSnapshot | None = None
    passengers: list[Passenger] = Field(min_length=1, max_length=9)
    contact: Contact
    totalPrice: int = Field(gt=0)
    currency: str = "INR"
    userId: str | None = None


class StatusUpdate(BaseModel):
    status: BookingStatus | None = None
    paymentStatus: PaymentStatus | None = None
    paymentId: str | None = None


def _new_id() -> str:
    return "BK" + uuid4().hex[:10].upper()


@app.get("/health")
def health():
    return {"status": "UP", "service": "booking"}


@app.post("/api/bookings", status_code=201)
def create_booking(payload: CreateBookingRequest):
    if payload.outboundFlight.flightId != payload.flightId:
        raise HTTPException(status_code=400, detail="flightId must match the selected outbound flight.")
    names = [(p.firstName.strip(), p.lastName.strip()) for p in payload.passengers]
    if any(not a or not b for a, b in names):
        raise HTTPException(status_code=400, detail="Passenger first and last names are required.")
    phone = payload.contact.phone.strip()
    if not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        raise HTTPException(status_code=400, detail="Enter a valid contact phone number.")

    booking_id = _new_id()
    record = {
        "bookingId": booking_id,
        "flightId": payload.flightId,
        "outboundFlight": payload.outboundFlight.model_dump(),
        "inboundFlight": payload.inboundFlight.model_dump() if payload.inboundFlight else None,
        "passengers": [p.model_dump() for p in payload.passengers],
        "contact": payload.contact.model_dump(),
        "totalPrice": payload.totalPrice,
        "currency": payload.currency,
        "userId": payload.userId,
        "bookingStatus": "PENDING",
        "paymentStatus": "UNPAID",
        "paymentId": None,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
    with _LOCK:
        _STORE[booking_id] = record
    return record


@app.get("/api/bookings/{booking_id}")
def get_booking(booking_id: str):
    with _LOCK:
        record = _STORE.get(booking_id)
    if not record:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return record


@app.post("/api/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: str):
    with _LOCK:
        record = _STORE.get(booking_id)
        if not record:
            raise HTTPException(status_code=404, detail="Booking not found.")
        if record["bookingStatus"] == "CANCELLED":
            raise HTTPException(status_code=400, detail="Booking is already cancelled.")
        record["bookingStatus"] = "CANCELLED"
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()
        return record


@app.post("/api/bookings/{booking_id}/confirm")
def confirm_booking(booking_id: str, payload: StatusUpdate | None = None):
    with _LOCK:
        record = _STORE.get(booking_id)
        if not record:
            raise HTTPException(status_code=404, detail="Booking not found.")
        if record["bookingStatus"] == "CANCELLED":
            raise HTTPException(status_code=400, detail="Cancelled bookings cannot be confirmed.")
        record["bookingStatus"] = "CONFIRMED"
        record["paymentStatus"] = (payload.paymentStatus if payload and payload.paymentStatus else "SUCCESS")
        if payload and payload.paymentId:
            record["paymentId"] = payload.paymentId
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()
        return record


@app.patch("/api/bookings/{booking_id}")
def update_booking(booking_id: str, payload: StatusUpdate):
    with _LOCK:
        record = _STORE.get(booking_id)
        if not record:
            raise HTTPException(status_code=404, detail="Booking not found.")
        if payload.status:
            record["bookingStatus"] = payload.status
        if payload.paymentStatus:
            record["paymentStatus"] = payload.paymentStatus
        if payload.paymentId:
            record["paymentId"] = payload.paymentId
        record["updatedAt"] = datetime.now(timezone.utc).isoformat()
        return record
