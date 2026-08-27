import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import App from "./App.jsx";
import SearchForm from "./components/SearchForm.jsx";
import FlightCard from "./components/FlightCard.jsx";
import ConfirmationPage from "./pages/ConfirmationPage.jsx";
import PaymentPage from "./pages/PaymentPage.jsx";
import BookingPage from "./pages/BookingPage.jsx";
import { SESSION_KEYS } from "./api.js";

function renderApp(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe("search form", () => {
  it("renders trip type and search controls", () => {
    render(<SearchForm onSearch={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Search Flights" })).toBeInTheDocument();
    expect(screen.getByLabelText("From")).toBeInTheDocument();
    expect(screen.getByLabelText("To")).toBeInTheDocument();
    expect(screen.getByLabelText("Adults")).toBeInTheDocument();
  });

  it("blocks same origin and destination", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} initial={{
      tripType: "ONE_WAY",
      from: "DEL",
      fromLabel: "Delhi (DEL)",
      to: "DEL",
      toLabel: "Delhi (DEL)",
      departureDate: "2026-09-10",
      returnDate: "",
      adults: 1,
      children: 0,
      infants: 0,
      cabinClass: "ECONOMY",
    }} />);
    await userEvent.click(screen.getByRole("button", { name: "Search Flights" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/must be different/i);
    expect(onSearch).not.toHaveBeenCalled();
  });
});

describe("pages", () => {
  it("shows homepage hero", () => {
    renderApp("/");
    expect(screen.getByRole("heading", { name: /fly somewhere/i })).toBeInTheDocument();
  });

  it("renders a flight result card", async () => {
    const onSelect = vi.fn();
    render(
      <FlightCard
        flight={{
          flightId: "AI-1",
          airline: "Air India",
          airlineCode: "AI",
          flightNumber: "AI131",
          origin: "DEL",
          originCity: "Delhi",
          destination: "BOM",
          destinationCity: "Mumbai",
          departureTime: "2026-09-10T06:30:00Z",
          arrivalTime: "2026-09-10T08:45:00Z",
          duration: "2h 15m",
          stopLabel: "Non-stop",
          price: 6450,
          cabinClass: "ECONOMY",
        }}
        onSelect={onSelect}
      />
    );
    expect(screen.getByText("Air India")).toBeInTheDocument();
    expect(screen.getByText(/6,450/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Select" }));
    expect(onSelect).toHaveBeenCalled();
  });

  it("booking page empty state", () => {
    sessionStorage.clear();
    render(
      <MemoryRouter>
        <BookingPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/no flight selected/i)).toBeInTheDocument();
  });

  it("payment page empty state", () => {
    sessionStorage.clear();
    render(
      <MemoryRouter>
        <PaymentPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/no pending booking/i)).toBeInTheDocument();
  });

  it("confirmation page shows booking details", () => {
    sessionStorage.setItem(
      SESSION_KEYS.booking,
      JSON.stringify({
        bookingId: "BKTEST",
        bookingStatus: "CONFIRMED",
        paymentStatus: "SUCCESS",
        totalPrice: 6450,
        contact: { email: "user@example.com" },
        passengers: [{ firstName: "Asha", lastName: "Mehta" }],
        outboundFlight: {
          airline: "Air India",
          flightNumber: "AI131",
          origin: "DEL",
          destination: "BOM",
          departureTime: "2026-09-10T06:30:00Z",
          arrivalTime: "2026-09-10T08:45:00Z",
        },
      })
    );
    sessionStorage.setItem(SESSION_KEYS.payment, JSON.stringify({ status: "SUCCESS" }));
    render(
      <MemoryRouter>
        <ConfirmationPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/booking confirmed/i)).toBeInTheDocument();
    expect(screen.getByText("BKTEST")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /print confirmation/i })).toBeInTheDocument();
  });
});
