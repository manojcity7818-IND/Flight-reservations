const API_BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!response.ok) {
    const message = typeof data?.detail === "string" ? data.detail : "Something went wrong. Please try again.";
    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

export const api = {
  airports: (q = "") => request(`/airports${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  searchFlights: (params) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, String(value));
      }
    });
    return request(`/flights?${query.toString()}`);
  },
  getFlight: (id, cabinClass = "ECONOMY") =>
    request(`/flights/${encodeURIComponent(id)}?cabinClass=${cabinClass}`),
  createUser: (body) => request("/users", { method: "POST", body: JSON.stringify(body) }),
  createBooking: (body) => request("/bookings", { method: "POST", body: JSON.stringify(body) }),
  getBooking: (id) => request(`/bookings/${encodeURIComponent(id)}`),
  confirmBooking: (id, body) =>
    request(`/bookings/${encodeURIComponent(id)}/confirm`, { method: "POST", body: JSON.stringify(body) }),
  cancelBooking: (id) => request(`/bookings/${encodeURIComponent(id)}/cancel`, { method: "POST" }),
  pay: (body) => request("/payments", { method: "POST", body: JSON.stringify(body) }),
  notify: (body) => request("/notifications", { method: "POST", body: JSON.stringify(body) }),
  listNotifications: (bookingId) =>
    request(`/notifications${bookingId ? `?bookingId=${encodeURIComponent(bookingId)}` : ""}`),
};

export function inr(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatClock(iso) {
  return new Date(iso).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false });
}

export function formatLongDate(iso) {
  return new Date(iso).toLocaleDateString("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export const SESSION_KEYS = {
  search: "mb.search",
  results: "mb.results",
  selection: "mb.selection",
  booking: "mb.booking",
  payment: "mb.payment",
};

export function saveSession(key, value) {
  sessionStorage.setItem(key, JSON.stringify(value));
}

export function loadSession(key, fallback = null) {
  const raw = sessionStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}
