"""Framework-free data access and search logic for Expedia Lite.

This module owns reading the CSV files and joining hotels to trips.
It has no knowledge of FastAPI, HTTP, or JSON responses -- it returns
plain Python dictionaries and lists so it can be tested on its own.
"""

import csv
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HOTELS_CSV = DATA_DIR / "hotels.csv"
TRIPS_CSV = DATA_DIR / "trips.csv"
USERS_CSV = DATA_DIR / "users.csv"
BOOKINGS_CSV = DATA_DIR / "bookings.csv"


def load_hotels(path: Path = HOTELS_CSV) -> list[dict]:
    """Read hotels.csv and return one dict per hotel row."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_trips(path: Path = TRIPS_CSV) -> list[dict]:
    """Read trips.csv and return one dict per trip row."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_users(path: Path = USERS_CSV) -> list[dict]:
    """Read users.csv and return one dict per demo traveler row."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_bookings(path: Path = BOOKINGS_CSV) -> list[dict]:
    """Read bookings.csv and return one dict per seeded booking row."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _nights(check_in: str, check_out: str) -> int:
    """Return the number of nights between two YYYY-MM-DD strings."""
    from datetime import date

    y1, m1, d1 = (int(part) for part in check_in.split("-"))
    y2, m2, d2 = (int(part) for part in check_out.split("-"))
    return (date(y2, m2, d2) - date(y1, m1, d1)).days


def search_trips_by_city(city: str, hotels: Optional[list] = None,
                          trips: Optional[list] = None) -> list[dict]:
    """Return trips whose hotel is in the given city (case-insensitive).

    Each result joins the trip with its hotel (via hotel_id) and adds
    the derived number of nights and estimated stay price.
    """
    hotels = load_hotels() if hotels is None else hotels
    trips = load_trips() if trips is None else trips

    hotels_by_id = {h["hotel_id"]: h for h in hotels}
    query = city.strip().lower()

    results = []
    for trip in trips:
        hotel = hotels_by_id.get(trip["hotel_id"])
        if hotel is None:
            continue
        if hotel["city"].strip().lower() != query:
            continue
        nights = _nights(trip["check_in"], trip["check_out"])
        rate = float(hotel["nightly_rate_usd"])
        results.append({
            "trip_id": trip["trip_id"],
            "trip_name": trip["trip_name"],
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "city": hotel["city"],
            "state": hotel["state"],
            "check_in": trip["check_in"],
            "check_out": trip["check_out"],
            "nights": nights,
            "nightly_rate_usd": rate,
            "stay_price_usd": round(nights * rate, 2),
        })
    return results
