"""Lightweight frontend contract tests (no browser required)."""

from pathlib import Path

WEB = Path(__file__).resolve().parents[1]


def test_routes_exist_in_app():
    app = (WEB / "src" / "App.jsx").read_text()
    for route in ["/", "/search", "/flights", "/booking", "/payment", "/confirmation"]:
        assert route in app


def test_search_form_has_required_fields():
    source = (WEB / "src" / "components" / "SearchForm.jsx").read_text()
    for token in ["Round trip", "One way", "Multi-city", "Search Flights", "Adults", "Children", "Infants"]:
        assert token in source


def test_confirmation_has_print():
    source = (WEB / "src" / "pages" / "ConfirmationPage.jsx").read_text()
    assert "Download / Print confirmation" in source
    assert "Booking confirmed" in source
