import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";

const CABINS = [
  { value: "ECONOMY", label: "Economy" },
  { value: "PREMIUM_ECONOMY", label: "Premium Economy" },
  { value: "BUSINESS", label: "Business" },
  { value: "FIRST", label: "First Class" },
];

function todayPlus(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export const defaultSearch = {
  tripType: "ROUND_TRIP",
  from: "DEL",
  fromLabel: "Delhi (DEL)",
  to: "BOM",
  toLabel: "Mumbai (BOM)",
  departureDate: todayPlus(14),
  returnDate: todayPlus(21),
  adults: 1,
  children: 0,
  infants: 0,
  cabinClass: "ECONOMY",
};

function AirportField({ id, label, value, display, onChange }) {
  const [query, setQuery] = useState(display || "");
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState([]);

  useEffect(() => {
    setQuery(display || "");
  }, [display]);

  useEffect(() => {
    const handle = setTimeout(async () => {
      try {
        const data = await api.airports(query);
        setOptions(data.airports || []);
      } catch {
        setOptions([]);
      }
    }, 150);
    return () => clearTimeout(handle);
  }, [query]);

  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        value={query}
        autoComplete="off"
        placeholder="City or airport"
        onFocus={() => setOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
      />
      {open && options.length > 0 && (
        <div className="suggest" role="listbox">
          {options.slice(0, 8).map((airport) => (
            <button
              type="button"
              key={airport.code}
              onClick={() => {
                const next = `${airport.city} (${airport.code})`;
                setQuery(next);
                onChange(airport.code, next);
                setOpen(false);
              }}
            >
              <strong>{airport.city}</strong> · {airport.code}
              <div className="muted">{airport.name}</div>
            </button>
          ))}
        </div>
      )}
      {value && <input type="hidden" name={id} value={value} />}
    </div>
  );
}

export default function SearchForm({ initial = defaultSearch, onSearch, compact = false }) {
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const passengers = form.adults + form.children + form.infants;

  const passengerLabel = useMemo(
    () => `${passengers} traveller${passengers === 1 ? "" : "s"} · ${CABINS.find((c) => c.value === form.cabinClass)?.label}`,
    [passengers, form.cabinClass]
  );

  function update(patch) {
    setForm((current) => ({ ...current, ...patch }));
  }

  function submit(event) {
    event.preventDefault();
    setError("");
    if (!form.from || !form.to) {
      setError("Choose origin and destination airports.");
      return;
    }
    if (form.from === form.to) {
      setError("Origin and destination must be different.");
      return;
    }
    if (!form.departureDate) {
      setError("Choose a departure date.");
      return;
    }
    if (form.tripType === "ROUND_TRIP" && !form.returnDate) {
      setError("Choose a return date for round trip.");
      return;
    }
    if (form.tripType === "ROUND_TRIP" && form.returnDate < form.departureDate) {
      setError("Return date cannot be before departure.");
      return;
    }
    if (form.adults < 1) {
      setError("At least one adult is required.");
      return;
    }
    onSearch({ ...form, passengers });
  }

  return (
    <form className="search-panel" onSubmit={submit} aria-label="Flight search">
      <div className="trip-tabs" role="tablist">
        {[
          ["ROUND_TRIP", "Round trip"],
          ["ONE_WAY", "One way"],
          ["MULTI_CITY", "Multi-city"],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            className={`chip ${form.tripType === value ? "active" : ""}`}
            onClick={() => update({ tripType: value, returnDate: value === "ONE_WAY" ? "" : form.returnDate || defaultSearch.returnDate })}
          >
            {label}
          </button>
        ))}
      </div>
      {form.tripType === "MULTI_CITY" && (
        <p className="muted">Add two cities below — we search each segment independently after you continue.</p>
      )}
      <div className="grid-form">
        <AirportField
          id="from"
          label="From"
          value={form.from}
          display={form.fromLabel}
          onChange={(code, label) => update({ from: code, fromLabel: label })}
        />
        <AirportField
          id="to"
          label="To"
          value={form.to}
          display={form.toLabel}
          onChange={(code, label) => update({ to: code, toLabel: label })}
        />
        <div className="field">
          <label htmlFor="departureDate">Departure</label>
          <input
            id="departureDate"
            type="date"
            value={form.departureDate}
            onChange={(e) => update({ departureDate: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="returnDate">Return</label>
          <input
            id="returnDate"
            type="date"
            disabled={form.tripType === "ONE_WAY"}
            value={form.tripType === "ONE_WAY" ? "" : form.returnDate}
            onChange={(e) => update({ returnDate: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="cabinClass">Travellers & class</label>
          <select
            id="cabinClass"
            value={form.cabinClass}
            onChange={(e) => update({ cabinClass: e.target.value })}
            aria-label={passengerLabel}
          >
            {CABINS.map((cabin) => (
              <option key={cabin.value} value={cabin.value}>
                {cabin.label}
              </option>
            ))}
          </select>
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <label>
              Adults
              <input
                type="number"
                min="1"
                max="9"
                value={form.adults}
                onChange={(e) => update({ adults: Number(e.target.value) })}
                aria-label="Adults"
              />
            </label>
            <label>
              Children
              <input
                type="number"
                min="0"
                max="8"
                value={form.children}
                onChange={(e) => update({ children: Number(e.target.value) })}
                aria-label="Children"
              />
            </label>
            <label>
              Infants
              <input
                type="number"
                min="0"
                max="4"
                value={form.infants}
                onChange={(e) => update({ infants: Number(e.target.value) })}
                aria-label="Infants"
              />
            </label>
          </div>
        </div>
        <button className="btn" type="submit">
          Search Flights
        </button>
      </div>
      {error && (
        <div className="error-banner" role="alert" style={{ margin: "12px 0 0" }}>
          {error}
        </div>
      )}
      {!compact && <p className="muted">Fares shown later are sample inventory in INR — no live airline connection.</p>}
    </form>
  );
}
