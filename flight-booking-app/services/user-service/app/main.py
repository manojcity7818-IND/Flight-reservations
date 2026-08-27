from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="My Booking Users", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STORE: dict[str, dict] = {}
_LOCK = Lock()


class CreateUserRequest(BaseModel):
    firstName: str = Field(min_length=1, max_length=60)
    lastName: str = Field(min_length=1, max_length=60)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=20)


@app.get("/health")
def health():
    return {"status": "UP", "service": "user"}


@app.post("/api/users", status_code=201)
def create_user(payload: CreateUserRequest):
    phone_digits = payload.phone.replace("+", "").replace("-", "").replace(" ", "")
    if not phone_digits.isdigit():
        raise HTTPException(status_code=400, detail="Enter a valid phone number.")
    user_id = "US" + uuid4().hex[:10].upper()
    record = {
        "userId": user_id,
        "firstName": payload.firstName.strip(),
        "lastName": payload.lastName.strip(),
        "email": str(payload.email).lower(),
        "phone": payload.phone.strip(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    with _LOCK:
        _STORE[user_id] = record
    return record


@app.get("/api/users/{user_id}")
def get_user(user_id: str):
    with _LOCK:
        record = _STORE.get(user_id)
    if not record:
        raise HTTPException(status_code=404, detail="User not found.")
    return record
