# My Booking — Flight Booking App

Standalone flight-search and booking platform (brand: **My Booking**). It is a new application, separate from any Hotel Reservation system.

Inspired by modern flight-search UX. It does **not** copy Skyscanner (or any airline) branding, assets, or source.

## Why this stack

This repository did not contain a runnable Hotel Reservation codebase (only a short root README). The Hotel screenshot/reference layout used **independent service folders**, **Docker Compose**, **nginx for the web app**, and **pytest**. To stay compatible with that DevOps shape:

- **Backend:** Python 3.12 + FastAPI (lightweight, easy to containerize, pytest-native)
- **Frontend:** React + Vite, served by nginx
- **Local orchestration:** Docker Compose
- **CI:** Azure DevOps YAML (CI and PR validation only — no AKS/CD)

## Architecture

```
                 My Booking UI (React / nginx)
                           |
                           v
                    API Gateway (FastAPI)
                           |
        +------------------+------------------+
        |          |          |        |       |
        v          v          v        v       v
     Flight     Booking    Payment Notification User
     Search     Service    Service    Service   Service
        |
        v
    Mock flight inventory
```

## Local URLs

| Surface | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| API gateway | http://localhost:8080 |
| Flight search | http://localhost:8001 |
| Booking | http://localhost:8002 |
| Payment | http://localhost:8003 |
| Notification | http://localhost:8004 |
| User | http://localhost:8005 |

Health: `GET http://localhost:8001/health` (and the same path on each service).

## Docker Compose

```bash
cd flight-booking-app
docker compose up --build
docker compose down
```

Services talk to each other with Compose **service names** (never `localhost` inside containers). The gateway uses `http://flight-search-service:8000`, etc.

## Run without Docker

```bash
# terminals, one per service
cd services/flight-search-service && uvicorn app.main:app --port 8001
cd services/booking-service && uvicorn app.main:app --port 8002
cd services/payment-service && uvicorn app.main:app --port 8003
cd services/notification-service && uvicorn app.main:app --port 8004
cd services/user-service && uvicorn app.main:app --port 8005
FLIGHT_SEARCH_URL=http://127.0.0.1:8001 BOOKING_SERVICE_URL=http://127.0.0.1:8002 \
PAYMENT_SERVICE_URL=http://127.0.0.1:8003 NOTIFICATION_SERVICE_URL=http://127.0.0.1:8004 \
USER_SERVICE_URL=http://127.0.0.1:8005 \
uvicorn app.main:app --app-dir services/api-gateway --port 8080
cd web && npm install && VITE_PROXY_TARGET=http://127.0.0.1:8080 npm run dev
```

Open http://localhost:5173

## Tests

```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

Or per service: `(cd services/flight-search-service && pytest)`

Frontend: `(cd web && npm test && npm run build)`

## Environment variables

See `.env.example`. No real secrets, Azure credentials, or payment keys are required.

| Variable | Used by | Purpose |
| --- | --- | --- |
| `FLIGHT_SEARCH_URL` | api-gateway | Upstream search service |
| `BOOKING_SERVICE_URL` | api-gateway | Upstream booking service |
| `PAYMENT_SERVICE_URL` | api-gateway | Upstream payment service |
| `NOTIFICATION_SERVICE_URL` | api-gateway | Upstream notification service |
| `USER_SERVICE_URL` | api-gateway | Upstream user service |
| `PAYMENT_DEFAULT_OUTCOME` | payment-service | `SUCCESS` or `FAILED` default |
| `VITE_API_BASE` | frontend build | API prefix, default `/api` |

## Sample API

```bash
curl "http://localhost:8080/api/flights?from=DEL&to=BOM&departureDate=2026-09-10"
curl -X POST http://localhost:8080/api/payments \
  -H 'Content-Type: application/json' \
  -d '{"bookingId":"BK12345","amount":6450,"currency":"INR","simulateOutcome":"SUCCESS"}'
```

Payment is simulated. Choose the demo instrument ending `4242` for success or `0000` for failure. Never enter a real card number.

## CI / PR pipelines

- `azure-pipelines-ci.yml` — main-branch CI: tests, frontend build, Docker image builds (no push, no deploy)
- `azure-pipelines-pr.yml` — pull request validation: lint, tests, build, Dockerfile validation

Point Azure DevOps at these files. Use pipeline variables/service connections later for ACR; do not hardcode secrets.

## What is intentionally not included

- Kubernetes / AKS / Helm / Ingress / Application Gateway
- Path-based `/flights` reverse proxy in Azure
- Real airline, email, SMS, or payment-provider integrations
