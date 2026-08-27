# Flight reservations

This repository hosts the **My Booking** flight booking application.

- Application: [`flight-booking-app/`](./flight-booking-app/)
- Local start: `cd flight-booking-app && docker compose up --build` then open http://localhost:3100
- Docs: [`flight-booking-app/README.md`](./flight-booking-app/README.md)
- CI: [`azure-pipelines-ci.yml`](./azure-pipelines-ci.yml)
- PR validation: [`azure-pipelines-pr.yml`](./azure-pipelines-pr.yml)

Hotel Reservation, if added later, should remain a **separate** application and must not be rewritten as part of the flight work.
