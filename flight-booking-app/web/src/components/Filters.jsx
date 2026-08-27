export default function Filters({ value, onChange, airlines }) {
  function toggleList(key, item) {
    const current = new Set(value[key] || []);
    if (current.has(item)) current.delete(item);
    else current.add(item);
    onChange({ ...value, [key]: Array.from(current) });
  }

  return (
    <aside className="side-card filters" aria-label="Filters">
      <h3>Filter</h3>
      <div className="filter-group">
        <strong>Stops</strong>
        {[
          [0, "Non-stop"],
          [1, "1 stop"],
        ].map(([stops, label]) => (
          <label key={stops}>
            <input
              type="checkbox"
              checked={(value.stops || []).includes(stops)}
              onChange={() => toggleList("stops", stops)}
            />
            {label}
          </label>
        ))}
      </div>
      <div className="filter-group">
        <strong>Airlines</strong>
        {airlines.map((airline) => (
          <label key={airline.code}>
            <input
              type="checkbox"
              checked={(value.airlines || []).includes(airline.code)}
              onChange={() => toggleList("airlines", airline.code)}
            />
            {airline.name}
          </label>
        ))}
      </div>
      <div className="filter-group">
        <strong>Departure</strong>
        {["morning", "afternoon", "evening", "night"].map((bucket) => (
          <label key={bucket}>
            <input
              type="checkbox"
              checked={(value.departureTime || []).includes(bucket)}
              onChange={() => toggleList("departureTime", bucket)}
            />
            {bucket[0].toUpperCase() + bucket.slice(1)}
          </label>
        ))}
      </div>
      <div className="filter-group">
        <strong>Max price (₹)</strong>
        <input
          type="number"
          min="0"
          value={value.maxPrice || ""}
          onChange={(e) => onChange({ ...value, maxPrice: e.target.value })}
          aria-label="Maximum price"
        />
      </div>
      <div className="filter-group">
        <strong>Max duration (minutes)</strong>
        <input
          type="number"
          min="0"
          value={value.maxDuration || ""}
          onChange={(e) => onChange({ ...value, maxDuration: e.target.value })}
          aria-label="Maximum duration"
        />
      </div>
    </aside>
  );
}
