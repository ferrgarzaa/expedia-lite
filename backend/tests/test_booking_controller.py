"""Tests for the database controller: booking create, read, update, delete."""

import pytest

from app.controllers import booking_controller
from app.controllers.booking_controller import BookingError
from app.database import init_db, seed_if_empty
from app.models import Booking


def test_seeded_history_is_readable(seeded_db):
    records = booking_controller.list_bookings(db_path=seeded_db)
    ids = {r.booking.booking_id for r in records}
    assert "B001" in ids
    assert len(records) == 6


def test_history_rows_resolve_traveler_and_stay(seeded_db):
    row = booking_controller.get_booking("B001", seeded_db).to_dict()
    assert row["traveler"]
    assert row["hotel_name"]
    assert row["nights"] > 0


def test_create_assigns_a_new_unique_id_and_keeps_seeded_ids(seeded_db):
    before = {
        r.booking.booking_id
        for r in booking_controller.list_bookings(db_path=seeded_db)
    }
    created = booking_controller.create_booking("U002", "T004", db_path=seeded_db)
    after = {
        r.booking.booking_id
        for r in booking_controller.list_bookings(db_path=seeded_db)
    }
    assert created.booking.booking_id not in before
    assert before < after
    assert created.booking.status == Booking.CONFIRMED


def test_create_rejects_an_unknown_traveler(seeded_db):
    with pytest.raises(BookingError):
        booking_controller.create_booking("U999", "T001", db_path=seeded_db)


def test_create_rejects_an_unknown_stay(seeded_db):
    with pytest.raises(BookingError):
        booking_controller.create_booking("U001", "T999", db_path=seeded_db)


def test_create_rejects_a_duplicate_confirmed_booking(seeded_db):
    booking_controller.create_booking("U002", "T004", db_path=seeded_db)
    with pytest.raises(BookingError):
        booking_controller.create_booking("U002", "T004", db_path=seeded_db)


def test_cancel_updates_status_and_keeps_the_record(seeded_db):
    created = booking_controller.create_booking("U002", "T004", db_path=seeded_db)
    booking_id = created.booking.booking_id

    cancelled = booking_controller.cancel_booking(booking_id, seeded_db)
    assert cancelled.booking.status == Booking.CANCELLED

    still_there = booking_controller.get_booking(booking_id, seeded_db)
    assert still_there is not None
    assert still_there.booking.status == Booking.CANCELLED


def test_update_rejects_an_invalid_status(seeded_db):
    with pytest.raises(BookingError):
        booking_controller.update_booking_status("B001", "refunded", seeded_db)


def test_delete_removes_only_that_booking(seeded_db):
    created = booking_controller.create_booking("U002", "T004", db_path=seeded_db)
    booking_id = created.booking.booking_id

    booking_controller.delete_booking(booking_id, seeded_db)

    assert booking_controller.get_booking(booking_id, seeded_db) is None
    assert booking_controller.get_booking("B001", seeded_db) is not None


def test_delete_rejects_an_unknown_booking(seeded_db):
    with pytest.raises(BookingError):
        booking_controller.delete_booking("B999", seeded_db)


def test_changes_survive_a_restart_and_seeding_never_runs_twice(seeded_db):
    created = booking_controller.create_booking("U002", "T004", db_path=seeded_db)
    booking_controller.cancel_booking("B001", seeded_db)
    booking_controller.delete_booking("B002", seeded_db)

    # Simulate restarting the backend: init + seed run again on startup.
    init_db(seeded_db)
    assert seed_if_empty(seeded_db) is False

    ids = {
        r.booking.booking_id
        for r in booking_controller.list_bookings(db_path=seeded_db)
    }
    assert created.booking.booking_id in ids     # addition survived
    assert "B002" not in ids                     # deletion survived
    assert (
        booking_controller.get_booking("B001", seeded_db).booking.status
        == Booking.CANCELLED                     # update survived
    )
    assert len(ids) == 6                         # no duplicated starter rows
