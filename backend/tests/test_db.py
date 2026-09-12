"""Tests for the SQLite persistence layer (app/db.py).

Each test gets its own temporary database file so these tests never
touch the real backend/data/expedia_lite.db.
"""

import pytest

from app import db


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    connection = db.get_connection(db_path)
    db.init_db(connection)
    db.seed_if_empty(connection)
    yield connection
    connection.close()


def test_seed_is_idempotent(conn):
    first_count = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    seeded_again = db.seed_if_empty(conn)
    second_count = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    assert seeded_again is False
    assert first_count == second_count


def test_search_boston_returns_four_trips(conn):
    ids = {t["trip_id"] for t in db.search_trips_by_city(conn, "Boston")}
    assert ids == {"T001", "T002", "T009", "T010"}


def test_search_is_case_insensitive(conn):
    lower = {t["trip_id"] for t in db.search_trips_by_city(conn, "boston")}
    upper = {t["trip_id"] for t in db.search_trips_by_city(conn, "BOSTON")}
    assert lower == upper


def test_search_city_with_no_trips_returns_empty(conn):
    assert db.search_trips_by_city(conn, "Miami") == []


def test_create_booking_assigns_new_unique_id(conn):
    before_ids = {b["booking_id"] for b in db.list_bookings(conn)}
    new_booking = db.create_booking(conn, user_id="U001", trip_id="T001")
    assert new_booking["booking_id"] not in before_ids
    assert new_booking["status"] == "confirmed"

    after_ids = {b["booking_id"] for b in db.list_bookings(conn)}
    assert new_booking["booking_id"] in after_ids


def test_new_booking_appears_in_history(conn):
    new_booking = db.create_booking(conn, user_id="U001", trip_id="T001")
    history = db.list_bookings(conn)
    match = [b for b in history if b["booking_id"] == new_booking["booking_id"]]
    assert len(match) == 1
    assert match[0]["user_id"] == "U001"
    assert match[0]["trip_id"] == "T001"


def test_cancel_booking_keeps_the_record(conn):
    new_booking = db.create_booking(conn, user_id="U001", trip_id="T001")
    updated = db.update_booking_status(conn, new_booking["booking_id"], "cancelled")
    assert updated["status"] == "cancelled"

    still_there = [b for b in db.list_bookings(conn)
                   if b["booking_id"] == new_booking["booking_id"]]
    assert len(still_there) == 1
    assert still_there[0]["status"] == "cancelled"


def test_update_unknown_booking_returns_none(conn):
    assert db.update_booking_status(conn, "B999", "cancelled") is None


def test_delete_booking_removes_it(conn):
    new_booking = db.create_booking(conn, user_id="U001", trip_id="T001")
    removed = db.delete_booking(conn, new_booking["booking_id"])
    assert removed is True

    remaining_ids = {b["booking_id"] for b in db.list_bookings(conn)}
    assert new_booking["booking_id"] not in remaining_ids


def test_delete_unknown_booking_returns_false(conn):
    assert db.delete_booking(conn, "B999") is False


def test_restart_does_not_duplicate_or_lose_changes(tmp_path):
    """Simulates stopping and restarting the app against the same DB file."""
    db_path = tmp_path / "restart.db"

    # First "app start": init + seed + add one booking.
    first_conn = db.get_connection(db_path)
    db.init_db(first_conn)
    db.seed_if_empty(first_conn)
    seeded_count = len(db.list_bookings(first_conn))
    new_booking = db.create_booking(first_conn, user_id="U001", trip_id="T001")
    first_conn.close()

    # Second "app start": same DB file, same startup sequence.
    second_conn = db.get_connection(db_path)
    db.init_db(second_conn)
    reseeded = db.seed_if_empty(second_conn)
    bookings_after_restart = db.list_bookings(second_conn)
    second_conn.close()

    assert reseeded is False
    assert len(bookings_after_restart) == seeded_count + 1
    assert any(b["booking_id"] == new_booking["booking_id"] for b in bookings_after_restart)
