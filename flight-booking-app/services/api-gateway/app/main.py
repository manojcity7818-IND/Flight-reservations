from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My Booking API Gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FLIGHT_SEARCH_URL = os.getenv("FLIGHT_SEARCH_URL", "http://flight-search-service:8000")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://booking-service:8000")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

PREFIX_MAP = (
    ("/api/flights", FLIGHT_SEARCH_URL),
    ("/api/airports", FLIGHT_SEARCH_URL),
    ("/api/bookings", BOOKING_SERVICE_URL),
    ("/api/payments", PAYMENT_SERVICE_URL),
    ("/api/notifications", NOTIFICATION_SERVICE_URL),
    ("/api/users", USER_SERVICE_URL),
)


@app.get("/health")
def health():
    return {"status": "UP", "service": "api-gateway"}


def _backend_for(path: str) -> str | None:
    for prefix, url in PREFIX_MAP:
        if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + "?"):
            return url
    return None


@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    path = "/api/" + full_path
    backend = _backend_for(path)
    if not backend:
        raise HTTPException(status_code=404, detail="No upstream service for this path.")

    url = f"{backend}{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            upstream = await client.request(
                request.method,
                url,
                headers=headers,
                content=body,
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Upstream service is unavailable.") from exc

    excluded = {"content-encoding", "transfer-encoding", "connection"}
    response_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in excluded}
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)
