import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, inr, loadSession, saveSession, SESSION_KEYS } from "../api.js";

function emptyPassenger() {
  return { firstName: "", lastName: "", type: "ADULT" };
}

export default function BookingPage() {
  const navigate = useNavigate();
  const selection = loadSession(SESSION_KEYS.selection);
  const count = selection?.search?.passengers || 1;
  const [passengers, setPassengers] = useState(Array.from({ length: count }, emptyPassenger));
  const [email, setEmail] = useState("guest@example.com");
  const [phone, setPhone] = useState("9876501234");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const total = selection?.totalPrice || 0;

  const valid = useMemo(
    () => passengers.every((p) => p.firstName.trim() && p.lastName.trim()) && email.includes("@") && phone.length >= 8,
    [passengers, email, phone]
  );

  if (!selection?.outbound) {
    return (
      <main className="confirm">
        <div className="empty">
          No flight selected. <Link to="/">Start a search</Link>
        </div>
      </main>
    );
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (!valid) {
      setError("Enter valid passenger names, email, and phone.");
      return;
    }
    setBusy(true);
    try {
      const user = await api.createUser({
        firstName: passengers[0].firstName,
        lastName: passengers[0].lastName,
        email,
        phone,
      });
      const booking = await api.createBooking({
        flightId: selection.outbound.flightId,
        outboundFlight: {
          flightId: selection.outbound.flightId,
          airline: selection.outbound.airline,
          flightNumber: selection.outbound.flightNumber,
          origin: selection.outbound.origin,
          destination: selection.outbound.destination,
          departureTime: selection.outbound.departureTime,
          arrivalTime: selection.outbound.arrivalTime,
          cabinClass: selection.outbound.cabinClass,
          duration: selection.outbound.duration,
          stops: selection.outbound.stops,
        },
        inboundFlight: selection.inbound
          ? {
              flightId: selection.inbound.flightId,
              airline: selection.inbound.airline,
              flightNumber: selection.inbound.flightNumber,
              origin: selection.inbound.origin,
              destination: selection.inbound.destination,
              departureTime: selection.inbound.departureTime,
              arrivalTime: selection.inbound.arrivalTime,
              cabinClass: selection.inbound.cabinClass,
              duration: selection.inbound.duration,
              stops: selection.inbound.stops,
            }
          : null,
        passengers,
        contact: { email, phone },
        totalPrice: total,
        currency: "INR",
        userId: user.userId,
      });
      saveSession(SESSION_KEYS.booking, booking);
      navigate("/payment");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <div className="stepper">
        <span>1. Flights</span>
        <span className="on">2. Travellers</span>
        <span>3. Payment</span>
        <span>4. Confirmation</span>
      </div>
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
      <form className="checkout" onSubmit={submit}>
        <section className="side-card">
          <h2 className="serif">Passenger details</h2>
          {passengers.map((passenger, index) => (
            <div key={index} className="passenger-grid" style={{ marginBottom: 16 }}>
              <div className="field">
                <label>First name</label>
                <input
                  value={passenger.firstName}
                  onChange={(e) => {
                    const next = [...passengers];
                    next[index] = { ...next[index], firstName: e.target.value };
                    setPassengers(next);
                  }}
                  required
                />
              </div>
              <div className="field">
                <label>Last name</label>
                <input
                  value={passenger.lastName}
                  onChange={(e) => {
                    const next = [...passengers];
                    next[index] = { ...next[index], lastName: e.target.value };
                    setPassengers(next);
                  }}
                  required
                />
              </div>
            </div>
          ))}
          <div className="passenger-grid">
            <div className="field">
              <label htmlFor="email">Contact email</label>
              <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="field">
              <label htmlFor="phone">Phone</label>
              <input id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} required />
            </div>
          </div>
          <p className="notice">We’ll use this to show a simulated booking notification — no real email is sent.</p>
          <button className="btn" type="submit" disabled={busy || !valid}>
            {busy ? "Creating booking…" : "Review and pay"}
          </button>
        </section>
        <aside className="side-card">
          <h3>Booking summary</h3>
          <p>
            <strong>{selection.outbound.airline}</strong> {selection.outbound.flightNumber}
          </p>
          <p className="muted">
            {selection.outbound.origin} → {selection.outbound.destination}
          </p>
          {selection.inbound && (
            <p className="muted">
              Return {selection.inbound.origin} → {selection.inbound.destination}
            </p>
          )}
          <div className="row">
            <span>Travellers</span>
            <span>{count}</span>
          </div>
          <div className="row">
            <span>Total</span>
            <strong>{inr(total)}</strong>
          </div>
        </aside>
      </form>
    </main>
  );
}
