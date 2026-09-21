"""Database controller for booking CRUD.

Every create, read, update, and delete the interface performs on a
booking goes through exactly one of the functions below. Raising
``BookingError`` is how this layer reports a rule violation; the
FastAPI layer turns that into an HTTP status code.

New booking IDs continue the supplied ``B###`` sequence, so seeded IDs
are preserved and every new record still gets a unique one.
"""

from datetime import date
from pathlib import Path
from typing import List, Optional, Union

from app.controllers.travel_controller import get_stay, get_user
from app.database import get_connection
from app.models import Booking, BookingRecord, Hotel, StayOffer, Trip, User

_HISTORY_SQL = """
SELECT b.booking_id, b.user_id, b.trip_id, b.booked_on, b.status,
       u.display_name,
       t.hotel_id, t.trip_name, t.check_in, t.check_out,
       h.hotel_name, h.city, h.state, h.nightly_rate_usd
FROM bookings AS b
JOIN users AS u ON u.user_id = b.user_id
JOIN trips AS t ON t.trip_id = b.trip_id
JOIN hotels AS h ON h.hotel_id = t.hotel_id
"""


class BookingError(Exception):
    """A booking request that the rules of the application reject."""


def _record_from_row(row) -> BookingRecord:
    return BookingRecord(
        booking=Booking.from_row(row),
        user=User.from_row(row),
        offer=StayOffer(trip=Trip.from_row(row), hotel=Hotel.from_row(row)),
    )


def _next_booking_id(connection) -> str:
    """Return the next unused ``B###`` id, never reusing an existing one."""
    rows = connection.execute("SELECT booking_id FROM bookings").fetchall()
    highest = 0
    for row in rows:
        digits = row["booking_id"][1:]
        if row["booking_id"].startswith("B") and digits.isdigit():
            highest = max(highest, int(digits))
    return f"B{highest + 1:03d}"


# ---------------------------------------------------------------- READ
def list_bookings(
    user_id: Optional[str] = None, db_path: Optional[Union[Path, str]] = None
) -> List[BookingRecord]:
    """Return booking history, newest first, optionally for one traveler."""
    sql = _HISTORY_SQL
    params: tuple = ()
    if user_id:
        sql += " WHERE b.user_id = ?"
        params = (user_id,)
    sql += " ORDER BY b.booked_on DESC, b.booking_id DESC"

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [_record_from_row(row) for row in rows]


def get_booking(
    booking_id: str, db_path: Optional[Union[Path, str]] = None
) -> Optional[BookingRecord]:
    """Return one booking joined to its traveler and stay, or None."""
    with get_connection(db_path) as connection:
        row = connection.execute(
            _HISTORY_SQL + " WHERE b.booking_id = ?", (booking_id,)
        ).fetchone()
    return _record_from_row(row) if row else None


# -------------------------------------------------------------- CREATE
def create_booking(
    user_id: str,
    trip_id: str,
    booked_on: Optional[str] = None,
    db_path: Optional[Union[Path, str]] = None,
) -> BookingRecord:
    """Create a confirmed booking for a traveler and an offered stay."""
    if get_user(user_id, db_path) is None:
        raise BookingError(f"Unknown traveler {user_id!r}.")
    if get_stay(trip_id, db_path) is None:
        raise BookingError(f"Unknown stay {trip_id!r}.")

    with get_connection(db_path) as connection:
        duplicate = connection.execute(
            """SELECT booking_id FROM bookings
               WHERE user_id = ? AND trip_id = ? AND status = ?""",
            (user_id, trip_id, Booking.CONFIRMED),
        ).fetchone()
        if duplicate is not None:
            raise BookingError(
                f"That traveler already holds confirmed booking "
                f"{duplicate['booking_id']} for this stay."
            )

        booking_id = _next_booking_id(connection)
        connection.execute(
            "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
            (
                booking_id,
                user_id,
                trip_id,
                booked_on or date.today().isoformat(),
                Booking.CONFIRMED,
            ),
        )

    created = get_booking(booking_id, db_path)
    assert created is not None
    return created


# -------------------------------------------------------------- UPDATE
def update_booking_status(
    booking_id: str, status: str, db_path: Optional[Union[Path, str]] = None
) -> BookingRecord:
    """Update a booking's status, keeping the record itself.

    Cancelling is an update, not a delete: the row stays in history
    with ``status = 'cancelled'``.
    """
    normalised = status.strip().lower()
    if normalised not in Booking.VALID_STATUSES:
        raise BookingError(
            f"Status must be one of {', '.join(Booking.VALID_STATUSES)}."
        )
    if get_booking(booking_id, db_path) is None:
        raise BookingError(f"Unknown booking {booking_id!r}.")

    with get_connection(db_path) as connection:
        connection.execute(
            "UPDATE bookings SET status = ? WHERE booking_id = ?",
            (normalised, booking_id),
        )

    updated = get_booking(booking_id, db_path)
    assert updated is not None
    return updated


def cancel_booking(
    booking_id: str, db_path: Optional[Union[Path, str]] = None
) -> BookingRecord:
    """Convenience wrapper: the cancel action used by the interface."""
    return update_booking_status(booking_id, Booking.CANCELLED, db_path)


# -------------------------------------------------------------- DELETE
def delete_booking(booking_id: str, db_path: Optional[Union[Path, str]] = None) -> None:
    """Remove a booking row completely, leaving other records alone."""
    if get_booking(booking_id, db_path) is None:
        raise BookingError(f"Unknown booking {booking_id!r}.")
    with get_connection(db_path) as connection:
        connection.execute(
            "DELETE FROM bookings WHERE booking_id = ?", (booking_id,)
        )
