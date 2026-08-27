import { formatClock, inr } from "../api.js";

export default function FlightCard({ flight, selected, onSelect }) {
  return (
    <article className={`flight-card ${selected ? "selected" : ""}`}>
      <div className="airline">
        <div className="logo" style={{ background: flight.airlineColor || "#1c3348" }} aria-hidden="true">
          {flight.airlineCode}
        </div>
        <div>
          <strong>{flight.airline}</strong>
          <div className="muted">{flight.flightNumber}</div>
        </div>
      </div>
      <div>
        <div className="times">
          <div>
            <div className="time">{formatClock(flight.departureTime)}</div>
            <div className="muted">
              {flight.originCity} ({flight.origin})
            </div>
          </div>
          <div className="bar">
            <span>
              {flight.duration} · {flight.stopLabel}
            </span>
          </div>
          <div>
            <div className="time">{formatClock(flight.arrivalTime)}</div>
            <div className="muted">
              {flight.destinationCity} ({flight.destination})
            </div>
          </div>
        </div>
      </div>
      <div className="price">
        <strong>{inr(flight.price)}</strong>
        <div className="muted">{flight.cabinClass.replaceAll("_", " ")}</div>
        <button className="btn" type="button" onClick={() => onSelect(flight)}>
          Select
        </button>
      </div>
    </article>
  );
}
