from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("notification-service")

app = FastAPI(title="My Booking Notifications", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NotificationType = Literal["BOOKING_CONFIRMATION", "PAYMENT_CONFIRMATION", "CANCELLATION"]

_STORE: list[dict] = []
_LOCK = Lock()


class NotificationRequest(BaseModel):
    bookingId: str = Field(min_length=3)
    type: NotificationType
    recipient: EmailStr
    message: str | None = None


@app.get("/health")
def health():
    return {"status": "UP", "service": "notification"}


@app.post("/api/notifications", status_code=201)
def send_notification(payload: NotificationRequest):
    templates = {
        "BOOKING_CONFIRMATION": f"Your My Booking reservation {payload.bookingId} is confirmed.",
        "PAYMENT_CONFIRMATION": f"Payment for booking {payload.bookingId} was received.",
        "CANCELLATION": f"Booking {payload.bookingId} has been cancelled.",
    }
    record = {
        "notificationId": "NT" + uuid4().hex[:10].upper(),
        "bookingId": payload.bookingId,
        "type": payload.type,
        "recipient": payload.recipient,
        "message": payload.message or templates[payload.type],
        "status": "SENT",
        "channel": "SIMULATED_EMAIL",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    logger.info(
        "Simulated notification sent type=%s bookingId=%s",
        payload.type,
        payload.bookingId,
    )
    with _LOCK:
        _STORE.append(record)
    return record


@app.get("/api/notifications")
def list_notifications(bookingId: str | None = None):
    with _LOCK:
        items = list(_STORE)
    if bookingId:
        items = [n for n in items if n["bookingId"] == bookingId]
    return {"notifications": items}


@app.get("/api/notifications/{notification_id}")
def get_notification(notification_id: str):
    with _LOCK:
        match = next((n for n in _STORE if n["notificationId"] == notification_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return match
