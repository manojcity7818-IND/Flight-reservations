import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatLongDate, inr, loadSession, SESSION_KEYS } from "../api.js";

export default function ConfirmationPage() {
  const booking = loadSession(SESSION_KEYS.booking);
  const payment = loadSession(SESSION_KEYS.payment);
  const [notes, setNotes] = useState([]);

  useEffect(() => {
    if (!booking?.bookingId) return;
    api
      .listNotifications(booking.bookingId)
      .then((data) => setNotes(data.notifications || []))
      .catch(() => setNotes([]));
  }, [booking?.bookingId]);

  if (!booking) {
    return (
      <main className="confirm">
        <div className="empty">
          Nothing to confirm yet. <Link to="/">Book a flight</Link>
        </div>
      </main>
    );
  }

  const passenger = booking.passengers?.[0];
  const flight = booking.outboundFlight;

  return (
    <main className="confirm">
      <div className="stamp" id="confirmation-ticket">
        <div className="kicker ok">Booking confirmed</div>
        <h1 className="serif">You’re on your way.</h1>
        <p className="muted">Keep this reference handy. A simulated confirmation was sent to {booking.contact.email}.</p>
        <div className="row">
          <span>Booking ID</span>
          <strong>{booking.bookingId}</strong>
        </div>
        <div className="row">
          <span>Passenger</span>
          <span>
            {passenger?.firstName} {passenger?.lastName}
          </span>
        </div>
        <div className="row">
          <span>Airline</span>
          <span>{flight.airline}</span>
        </div>
        <div className="row">
          <span>Flight</span>
          <span>{flight.flightNumber}</span>
        </div>
        <div className="row">
          <span>Origin</span>
          <span>{flight.origin}</span>
        </div>
        <div className="row">
          <span>Destination</span>
          <span>{flight.destination}</span>
        </div>
        <div className="row">
          <span>Departure</span>
          <span>{formatLongDate(flight.departureTime)}</span>
        </div>
        <div className="row">
          <span>Arrival</span>
          <span>{formatLongDate(flight.arrivalTime)}</span>
        </div>
        <div className="row">
          <span>Amount paid</span>
          <strong>{inr(booking.totalPrice)}</strong>
        </div>
        <div className="row">
          <span>Payment status</span>
          <span>{booking.paymentStatus || payment?.status}</span>
        </div>
        <h3>Notifications</h3>
        {notes.length === 0 && <p className="muted">No simulated messages found yet.</p>}
        <ul>
          {notes.map((note) => (
            <li key={note.notificationId}>
              {note.type}: {note.status}
            </li>
          ))}
        </ul>
        <div style={{ display: "flex", gap: 12, marginTop: 18 }}>
          <button className="btn secondary" type="button" onClick={() => window.print()}>
            Download / Print confirmation
          </button>
          <Link className="btn" to="/">
            Book another flight
          </Link>
        </div>
      </div>
    </main>
  );
}
