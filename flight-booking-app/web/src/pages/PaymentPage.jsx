import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, inr, loadSession, saveSession, SESSION_KEYS } from "../api.js";

export default function PaymentPage() {
  const navigate = useNavigate();
  const booking = loadSession(SESSION_KEYS.booking);
  const [method, setMethod] = useState("DEMO_CARD");
  const [instrument, setInstrument] = useState("demo-4242");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (!booking) {
    return (
      <main className="confirm">
        <div className="empty">
          No pending booking. <Link to="/">Search again</Link>
        </div>
      </main>
    );
  }

  async function pay(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payment = await api.pay({
        bookingId: booking.bookingId,
        amount: booking.totalPrice,
        currency: booking.currency || "INR",
        method,
        demoInstrument: instrument,
        simulateOutcome: instrument.endsWith("0000") ? "FAILED" : "SUCCESS",
      });
      saveSession(SESSION_KEYS.payment, payment);
      if (payment.status !== "SUCCESS") {
        await api.notify({
          bookingId: booking.bookingId,
          type: "CANCELLATION",
          recipient: booking.contact.email,
          message: "Simulated payment failed. Booking remains pending.",
        });
        setError("Payment failed. Try the successful demo instrument or start again.");
        return;
      }
      const confirmed = await api.confirmBooking(booking.bookingId, {
        paymentStatus: "SUCCESS",
        paymentId: payment.paymentId,
      });
      await api.notify({
        bookingId: booking.bookingId,
        type: "PAYMENT_CONFIRMATION",
        recipient: booking.contact.email,
      });
      await api.notify({
        bookingId: booking.bookingId,
        type: "BOOKING_CONFIRMATION",
        recipient: booking.contact.email,
      });
      saveSession(SESSION_KEYS.booking, confirmed);
      navigate("/confirmation");
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
        <span>2. Travellers</span>
        <span className="on">3. Payment</span>
        <span>4. Confirmation</span>
      </div>
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
      <form className="checkout" onSubmit={pay}>
        <section className="pay-card">
          <h2 className="serif">Simulated payment</h2>
          <p className="muted">
            This is a mock checkout. Do not enter real card numbers. Choose a demo instrument to succeed or fail.
          </p>
          <div className="field">
            <label htmlFor="method">Method</label>
            <select id="method" value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="DEMO_CARD">Demo card</option>
              <option value="UPI">UPI (simulated)</option>
              <option value="NET_BANKING">Net banking (simulated)</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="instrument">Demo instrument</label>
            <select id="instrument" value={instrument} onChange={(e) => setInstrument(e.target.value)}>
              <option value="demo-4242">Success · Demo Visa ending 4242</option>
              <option value="demo-0000">Failure · Demo card ending 0000</option>
            </select>
          </div>
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "Processing…" : `Pay ${inr(booking.totalPrice)}`}
          </button>
        </section>
        <aside className="side-card">
          <h3>Payment summary</h3>
          <div className="row">
            <span>Booking</span>
            <span>{booking.bookingId}</span>
          </div>
          <div className="row">
            <span>Status</span>
            <span>{booking.bookingStatus}</span>
          </div>
          <div className="row">
            <span>Amount</span>
            <strong>{inr(booking.totalPrice)}</strong>
          </div>
        </aside>
      </form>
    </main>
  );
}
