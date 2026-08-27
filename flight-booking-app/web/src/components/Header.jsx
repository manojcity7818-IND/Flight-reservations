import { NavLink } from "react-router-dom";

export default function Header() {
  return (
    <header className="header">
      <NavLink to="/" className="brand" aria-label="My Booking home">
        <span className="mark" aria-hidden="true">MB</span>
        <span>My Booking</span>
      </NavLink>
      <nav className="nav">
        <NavLink to="/" end>
          Flights
        </NavLink>
        <NavLink to="/search">Explore</NavLink>
      </nav>
    </header>
  );
}
