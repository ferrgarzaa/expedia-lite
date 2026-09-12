"""SQLite persistence for Expedia Lite (Part 2).

Framework-free: no FastAPI or HTTP here. This module owns the schema,
the one-time seed from the sample CSVs, and every read/write query.
`app/main.py` calls these functions and turns the results into JSON.
"""

import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from app.data import load_bookings, load_hotels, load_trips, load_users

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expedia_lite.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id TEXT PRIMARY KEY,
    hotel_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    nightly_rate_usd REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
    trip_name TEXT NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    trip_id TEXT NOT NULL REFERENCES trips(trip_id),
    booked_on TEXT NOT NULL,
    status TEXT NOT NULL
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a connection with row access by column name."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables if they do not already exist. Safe to call every startup."""
    conn.executescript(SCHEMA)
    conn.commit()


def seed_if_empty(conn: sqlite3.Connection) -> bool:
    """Seed hotels/trips/users/bookings from the sample CSVs exactly once.

    Returns True if seeding ran, False if the database already had data
    (so restarting the app never duplicates or reloads the starters).
    """
    existing = conn.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]
    if existing > 0:
        return False

    hotels = load_hotels()
    trips = load_trips()
    users = load_users()
    bookings = load_bookings()

    conn.executemany(
        "INSERT INTO hotels (hotel_id, hotel_name, city, state, nightly_rate_usd) "
        "VALUES (:hotel_id, :hotel_name, :city, :state, :nightly_rate_usd)",
        hotels,
    )
    conn.executemany(
        "INSERT INTO trips (trip_id, hotel_id, trip_name, check_in, check_out) "
        "VALUES (:trip_id, :hotel_id, :trip_name, :check_in, :check_out)",
        trips,
    )
    conn.executemany(
        "INSERT INTO users (user_id, display_name) VALUES (:user_id, :display_name)",
        users,
    )
    conn.executemany(
        "INSERT INTO bookings (booking_id, user_id, trip_id, booked_on, status) "
        "VALUES (:booking_id, :user_id, :trip_id, :booked_on, :status)",
        bookings,
    )
    conn.commit()
    return True


def _nights(check_in: str, check_out: str) -> int:
    y1, m1, d1 = (int(part) for part in check_in.split("-"))
    y2, m2, d2 = (int(part) for part in check_out.split("-"))
    return (date(y2, m2, d2) - date(y1, m1, d1)).days


def search_trips_by_city(conn: sqlite3.Connection, city: str) -> list[dict]:
    """Case-insensitive city search, joining trips to their hotel."""
    rows = conn.execute(
        """
        SELECT t.trip_id, t.trip_name, h.hotel_id, h.hotel_name,
               h.city, h.state, t.check_in, t.check_out, h.nightly_rate_usd
        FROM trips t
        JOIN hotels h ON h.hotel_id = t.hotel_id
        WHERE LOWER(TRIM(h.city)) = LOWER(TRIM(?))
        ORDER BY t.trip_id
        """,
        (city,),
    ).fetchall()

    results = []
    for row in rows:
        nights = _nights(row["check_in"], row["check_out"])
        rate = row["nightly_rate_usd"]
        results.append({
            **dict(row),
            "nights": nights,
            "stay_price_usd": round(nights * rate, 2),
        })
    return results


def list_users(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT user_id, display_name FROM users ORDER BY user_id").fetchall()
    return [dict(row) for row in rows]


def list_bookings(conn: sqlite3.Connection) -> list[dict]:
    """All bookings, joined with traveler and trip/hotel details, for history."""
    rows = conn.execute(
        """
        SELECT b.booking_id, b.booked_on, b.status,
               u.user_id, u.display_name,
               t.trip_id, t.trip_name, t.check_in, t.check_out,
               h.hotel_id, h.hotel_name, h.city, h.state
        FROM bookings b
        JOIN users u ON u.user_id = b.user_id
        JOIN trips t ON t.trip_id = b.trip_id
        JOIN hotels h ON h.hotel_id = t.hotel_id
        ORDER BY b.booking_id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def _next_booking_id(conn: sqlite3.Connection) -> str:
    """Generate the next unique booking ID, preserving the B### pattern."""
    rows = conn.execute("SELECT booking_id FROM bookings").fetchall()
    max_n = 0
    for row in rows:
        digits = "".join(ch for ch in row["booking_id"] if ch.isdigit())
        if digits:
            max_n = max(max_n, int(digits))
    return f"B{max_n + 1:03d}"


def create_booking(conn: sqlite3.Connection, user_id: str, trip_id: str) -> dict:
    """Create a new booking with status 'confirmed' and today's date."""
    booking_id = _next_booking_id(conn)
    booked_on = date.today().isoformat()
    conn.execute(
        "INSERT INTO bookings (booking_id, user_id, trip_id, booked_on, status) "
        "VALUES (?, ?, ?, ?, ?)",
        (booking_id, user_id, trip_id, booked_on, "confirmed"),
    )
    conn.commit()
    return {"booking_id": booking_id, "user_id": user_id, "trip_id": trip_id,
            "booked_on": booked_on, "status": "confirmed"}


def update_booking_status(conn: sqlite3.Connection, booking_id: str,
                           status: str) -> Optional[dict]:
    """Update a booking's status (e.g. cancel) while keeping the record."""
    cur = conn.execute(
        "UPDATE bookings SET status = ? WHERE booking_id = ?",
        (status, booking_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        return None
    row = conn.execute(
        "SELECT booking_id, user_id, trip_id, booked_on, status FROM bookings "
        "WHERE booking_id = ?",
        (booking_id,),
    ).fetchone()
    return dict(row)


def delete_booking(conn: sqlite3.Connection, booking_id: str) -> bool:
    """Delete a booking. Returns True if a row was removed."""
    cur = conn.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
    conn.commit()
    return cur.rowcount > 0
