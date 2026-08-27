import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import SearchForm, { defaultSearch } from "../components/SearchForm.jsx";
import FlightCard from "../components/FlightCard.jsx";
import Filters from "../components/Filters.jsx";
import { api, saveSession, SESSION_KEYS } from "../api.js";

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState({ outbound: [], inbound: [] });
  const [sort, setSort] = useState("best");
  const [filters, setFilters] = useState({ stops: [], airlines: [], departureTime: [], maxPrice: "", maxDuration: "" });
  const [outbound, setOutbound] = useState(null);
  const [inbound, setInbound] = useState(null);

  const form = {
    ...defaultSearch,
    from: params.get("from") || defaultSearch.from,
    to: params.get("to") || defaultSearch.to,
    fromLabel: params.get("from") || defaultSearch.fromLabel,
    toLabel: params.get("to") || defaultSearch.toLabel,
    departureDate: params.get("departureDate") || defaultSearch.departureDate,
    returnDate: params.get("returnDate") || "",
    tripType: params.get("tripType") || (params.get("returnDate") ? "ROUND_TRIP" : "ONE_WAY"),
    cabinClass: params.get("cabinClass") || "ECONOMY",
    adults: Number(params.get("passengers") || 1),
    passengers: Number(params.get("passengers") || 1),
    children: 0,
    infants: 0,
  };

  function applySearch(next) {
    const query = new URLSearchParams({
      from: next.from,
      to: next.to,
      departureDate: next.departureDate,
      passengers: String(next.passengers || next.adults + next.children + next.infants),
      cabinClass: next.cabinClass,
      tripType: next.tripType,
    });
    if (next.tripType !== "ONE_WAY" && next.returnDate) query.set("returnDate", next.returnDate);
    setParams(query);
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!params.get("from") || !params.get("to") || !params.get("departureDate")) {
        return;
      }
      setLoading(true);
      setError("");
      setOutbound(null);
      setInbound(null);
      try {
        const query = {
          from: params.get("from"),
          to: params.get("to"),
          departureDate: params.get("departureDate"),
          returnDate: params.get("returnDate") || undefined,
          passengers: params.get("passengers") || 1,
          cabinClass: params.get("cabinClass") || "ECONOMY",
          sort,
        };
        if (filters.stops.length) query.stops = filters.stops.join(",");
        if (filters.airlines.length) query.airlines = filters.airlines.join(",");
        if (filters.departureTime.length) query.departureTime = filters.departureTime.join(",");
        if (filters.maxPrice) query.maxPrice = filters.maxPrice;
        if (filters.maxDuration) query.maxDuration = filters.maxDuration;
        const data = await api.searchFlights(query);
        if (!cancelled) {
          setResults(data);
          saveSession(SESSION_KEYS.results, data);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [params, sort, filters]);

  const airlines = useMemo(() => {
    const map = new Map();
    [...(results.outbound || []), ...(results.inbound || [])].forEach((flight) => {
      map.set(flight.airlineCode, { code: flight.airlineCode, name: flight.airline });
    });
    return Array.from(map.values());
  }, [results]);

  const roundTrip = Boolean(params.get("returnDate"));

  function continueBooking() {
    if (!outbound) {
      setError("Select an outbound flight to continue.");
      return;
    }
    if (roundTrip && !inbound) {
      setError("Select a return flight to continue.");
      return;
    }
    const selection = {
      search: form,
      outbound,
      inbound,
      totalPrice: outbound.price + (inbound?.price || 0),
    };
    saveSession(SESSION_KEYS.selection, selection);
    navigate("/booking");
  }

  return (
    <main>
      <SearchForm initial={form} onSearch={applySearch} compact />
      <div className="stepper">
        <span className="on">1. Flights</span>
        <span>2. Travellers</span>
        <span>3. Payment</span>
        <span>4. Confirmation</span>
      </div>
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
      <div className="layout">
        <Filters value={filters} onChange={setFilters} airlines={airlines} />
        <section>
          <div className="sort-bar">
            <div>
              <h2 className="serif" style={{ margin: 0 }}>
                {form.from} → {form.to}
              </h2>
              <p className="muted">
                {loading ? "Searching sample fares…" : `${results.outbound?.length || 0} outbound flights`}
              </p>
            </div>
            <div className="sorts">
              {[
                ["best", "Best"],
                ["cheapest", "Cheapest"],
                ["fastest", "Fastest"],
                ["earliest", "Earliest departure"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  className={`chip ${sort === value ? "active" : ""}`}
                  onClick={() => setSort(value)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          {loading && <div className="loading">Finding flights…</div>}
          {!loading && results.outbound?.length === 0 && (
            <div className="empty">No flights found for this search. Try different dates, cities, or filters.</div>
          )}
          <h3>Outbound</h3>
          {(results.outbound || []).map((flight) => (
            <FlightCard
              key={flight.flightId}
              flight={flight}
              selected={outbound?.flightId === flight.flightId}
              onSelect={setOutbound}
            />
          ))}
          {roundTrip && (
            <>
              <h3>Return</h3>
              {(results.inbound || []).map((flight) => (
                <FlightCard
                  key={flight.flightId}
                  flight={flight}
                  selected={inbound?.flightId === flight.flightId}
                  onSelect={setInbound}
                />
              ))}
            </>
          )}
          <div style={{ marginTop: 16 }}>
            <button className="btn" type="button" onClick={continueBooking} disabled={!outbound}>
              Continue to traveller details
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
