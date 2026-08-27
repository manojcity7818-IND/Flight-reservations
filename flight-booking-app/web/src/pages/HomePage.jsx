import { useNavigate } from "react-router-dom";
import SearchForm, { defaultSearch } from "../components/SearchForm.jsx";
import { saveSession, SESSION_KEYS } from "../api.js";

const ROUTES = [
  { from: "DEL", to: "BOM", title: "Delhi → Mumbai", note: "Weekend hop" },
  { from: "BLR", to: "GOI", title: "Bengaluru → Goa", note: "Beach break" },
  { from: "BOM", to: "DXB", title: "Mumbai → Dubai", note: "City lights" },
  { from: "DEL", to: "SIN", title: "Delhi → Singapore", note: "Long weekend" },
];

export default function HomePage() {
  const navigate = useNavigate();

  function runSearch(form) {
    saveSession(SESSION_KEYS.search, form);
    const params = new URLSearchParams({
      from: form.from,
      to: form.to,
      departureDate: form.departureDate,
      passengers: String(form.passengers),
      cabinClass: form.cabinClass,
      tripType: form.tripType,
    });
    if (form.tripType !== "ONE_WAY" && form.returnDate) {
      params.set("returnDate", form.returnDate);
    }
    navigate(`/search?${params.toString()}`);
  }

  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="kicker">My Booking · Flights</div>
          <h1>Fly somewhere you’ll actually remember.</h1>
          <p className="lede">
            Search domestic and international sample fares, filter what matters, and complete a full booking
            with mock payment — built as a realistic travel experience for cloud deployment.
          </p>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="plane" />
        </div>
      </section>
      <SearchForm initial={defaultSearch} onSearch={runSearch} />
      <section className="popular">
        <h2 className="serif">Popular routes</h2>
        <div className="cards">
          {ROUTES.map((route) => (
            <button
              key={route.title}
              className="route-card"
              type="button"
              onClick={() =>
                runSearch({
                  ...defaultSearch,
                  from: route.from,
                  to: route.to,
                  fromLabel: route.from,
                  toLabel: route.to,
                  tripType: "ONE_WAY",
                  returnDate: "",
                  passengers: 1,
                })
              }
            >
              <div className="kicker">{route.note}</div>
              <h3>{route.title}</h3>
              <span className="muted">See sample fares</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
