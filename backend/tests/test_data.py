"""Tests for the framework-free search logic.

Expected trip IDs per city come from the instructor's sample data
README ("Concrete records to check" table).
"""

from app.data import search_trips_by_city


def test_boston_search_is_case_insensitive_and_returns_four_trips():
    lower = {t["trip_id"] for t in search_trips_by_city("boston")}
    upper = {t["trip_id"] for t in search_trips_by_city("Boston")}
    assert lower == upper == {"T001", "T002", "T009", "T010"}


def test_new_york_returns_three_trips():
    ids = {t["trip_id"] for t in search_trips_by_city("New York")}
    assert ids == {"T003", "T004", "T011"}


def test_state_college_returns_one_trip():
    ids = {t["trip_id"] for t in search_trips_by_city("State College")}
    assert ids == {"T008"}


def test_city_with_no_trips_returns_empty_list():
    assert search_trips_by_city("Miami") == []


def test_result_includes_joined_hotel_and_derived_fields():
    [result] = search_trips_by_city("State College")
    assert result["hotel_name"] == "Valley Trail Inn"
    assert result["nights"] == 2
    assert result["nightly_rate_usd"] == 100.0
    assert result["stay_price_usd"] == 200.0
