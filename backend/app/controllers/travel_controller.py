"""Read controller for hotels, stays, and travelers.

The Controller layer is the only place that talks to SQLite. It reads
rows, hands them to the Model classes, and returns Model objects. It
knows nothing about FastAPI or HTTP.
"""

from pathlib import Path

from app.database import get_connection
from app.models import Hotel, StayOffer, Trip, User

_OFFER_SQL = """
SELECT t.trip_id, t.hotel_id, t.trip_name, t.check_in, t.check_out,
       h.hotel_name, h.city, h.state, h.nightly_rate_usd
FROM trips AS t
JOIN hotels AS h ON h.hotel_id = t.hotel_id
"""


def _offer_from_row(row) -> StayOffer:
    return StayOffer(trip=Trip.from_row(row), hotel=Hotel.from_row(row))


def search_stays_by_hotel_name(
    hotel_name: str, db_path: Path | str | None = None
) -> list[StayOffer]:
    """Return the stays offered by hotels whose name matches the query.

    Matching is case-insensitive and partial, so "harbor" finds
    "Harbor Lantern Hotel". Results are ordered by hotel name and then
    check-in date so the table reads predictably.
    """
    query = hotel_name.strip().lower()
    if not query:
        return []

    sql = _OFFER_SQL + """
    WHERE LOWER(h.hotel_name) LIKE ?
    ORDER BY h.hotel_name, t.check_in
    """
    with get_connection(db_path) as connection:
        rows = connection.execute(sql, (f"%{query}%",)).fetchall()
    return [_offer_from_row(row) for row in rows]


def get_stay(trip_id: str, db_path: Path | str | None = None) -> StayOffer | None:
    """Return one offered stay joined to its hotel, or None."""
    sql = _OFFER_SQL + " WHERE t.trip_id = ?"
    with get_connection(db_path) as connection:
        row = connection.execute(sql, (trip_id,)).fetchone()
    return _offer_from_row(row) if row else None


def list_stays(db_path: Path | str | None = None) -> list[StayOffer]:
    """Return every offered stay joined to its hotel."""
    sql = _OFFER_SQL + " ORDER BY h.hotel_name, t.check_in"
    with get_connection(db_path) as connection:
        rows = connection.execute(sql).fetchall()
    return [_offer_from_row(row) for row in rows]


def list_users(db_path: Path | str | None = None) -> list[User]:
    """Return the demo travelers, used to populate the booking form."""
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT user_id, display_name FROM users ORDER BY user_id"
        ).fetchall()
    return [User.from_row(row) for row in rows]


def get_user(user_id: str, db_path: Path | str | None = None) -> User | None:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT user_id, display_name FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return User.from_row(row) if row else None
