"""SQLite connection, schema, and one-time seed for Expedia Lite.

This module is the storage plumbing the controllers sit on top of. It
opens connections, creates the tables, and seeds them **once** from the
supplied sample CSVs. It performs no CRUD of its own: creating,
reading, updating, and deleting records is the controllers' job.

Seeding rule (Assignment 1, Part 2): the CSVs are the initial data, not
a limit. ``seed_if_empty`` checks whether the tables already hold rows
and returns without touching them if they do, so restarting the app
never duplicates or reloads the starter records, and never discards
bookings added, cancelled, or deleted through the interface.
"""

import csv
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "expedia_lite.db"

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


def resolve_db_path(db_path: Path | str | None = None) -> Path:
    """Return the database file to use, defaulting to the app database."""
    return Path(db_path) if db_path else DB_PATH


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection with dict-style rows and foreign keys enforced."""
    db_path = resolve_db_path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: Path | str | None = None) -> None:
    """Create the tables if they do not exist yet."""
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA)


def _read_csv(name: str) -> list[dict]:
    with open(DATA_DIR / name, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def is_seeded(db_path: Path | str | None = None) -> bool:
    """True when the starter records are already in the database."""
    with get_connection(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]
    return count > 0


def seed_if_empty(db_path: Path | str | None = None) -> bool:
    """Seed the four tables from the sample CSVs, once.

    Returns True when this call inserted the starter records and False
    when the database was already seeded and was left untouched.
    """
    if is_seeded(db_path):
        return False

    hotels = _read_csv("hotels.csv")
    trips = _read_csv("trips.csv")
    users = _read_csv("users.csv")
    bookings = _read_csv("bookings.csv")

    with get_connection(db_path) as connection:
        connection.executemany(
            "INSERT INTO hotels VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["hotel_id"],
                    row["hotel_name"],
                    row["city"],
                    row["state"],
                    float(row["nightly_rate_usd"]),
                )
                for row in hotels
            ],
        )
        connection.executemany(
            "INSERT INTO trips VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["trip_id"],
                    row["hotel_id"],
                    row["trip_name"],
                    row["check_in"],
                    row["check_out"],
                )
                for row in trips
            ],
        )
        connection.executemany(
            "INSERT INTO users VALUES (?, ?)",
            [(row["user_id"], row["display_name"]) for row in users],
        )
        connection.executemany(
            "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["booking_id"],
                    row["user_id"],
                    row["trip_id"],
                    row["booked_on"],
                    row["status"].strip().lower(),
                )
                for row in bookings
            ],
        )
    return True
