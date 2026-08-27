from __future__ import annotations

import os
from datetime import datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="My Booking Mock Payments", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STORE: dict[str, dict] = {}
_LOCK = Lock()
DEFAULT_OUTCOME = os.getenv("PAYMENT_DEFAULT_OUTCOME", "SUCCESS").upper()


class PaymentRequest(BaseModel):
    bookingId: str = Field(min_length=3)
    amount: int = Field(gt=0)
    currency: str = "INR"
    method: Literal["DEMO_CARD", "UPI", "NET_BANKING"] = "DEMO_CARD"
    # Simulated outcome only — never a real card number
    simulateOutcome: Literal["SUCCESS", "FAILED"] | None = None
    demoInstrument: str | None = None


@app.get("/health")
def health():
    return {"status": "UP", "service": "payment"}


@app.post("/api/payments", status_code=201)
def create_payment(payload: PaymentRequest):
    if payload.currency.upper() not in {"INR", "USD", "EUR"}:
        raise HTTPException(status_code=400, detail="Unsupported currency.")

    outcome = (payload.simulateOutcome or DEFAULT_OUTCOME).upper()
    if payload.demoInstrument and payload.demoInstrument.endswith("0000"):
        outcome = "FAILED"
    if outcome not in {"SUCCESS", "FAILED"}:
        raise HTTPException(status_code=400, detail="simulateOutcome must be SUCCESS or FAILED.")

    payment_id = "PAY" + uuid4().hex[:10].upper()
    record = {
        "paymentId": payment_id,
        "bookingId": payload.bookingId,
        "amount": payload.amount,
        "currency": payload.currency.upper(),
        "method": payload.method,
        "status": outcome,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    with _LOCK:
        _STORE[payment_id] = record
    # Intentionally omit instrument details from logs and responses
    return record


@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: str):
    with _LOCK:
        record = _STORE.get(payment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return record
