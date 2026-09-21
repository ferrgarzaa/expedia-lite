"""Model layer for Expedia Lite (the "M" in Model-View-Controller).

The Model owns the application's data and the relationships between
records. It knows nothing about SQLite, FastAPI, HTTP, or Vue: each
class is a plain Python object that can be built from a database row
and turned back into a JSON-ready dictionary.

Relationships expressed here (they mirror the supplied sample data):

    Hotel  1 --- *  Trip        (Trip.hotel_id  -> Hotel.hotel_id)
    Trip   1 --- *  Booking     (Booking.trip_id -> Trip.trip_id)
    User   1 --- *  Booking     (Booking.user_id -> User.user_id)

A ``StayOffer`` is the joined view of one Trip together with the Hotel
it belongs to, plus the derived nights and stay price the interface
shows.
"""

from dataclasses import dataclass
from datetime import date


def _nights_between(check_in: str, check_out: str) -> int:
    """Return the number of nights between two ``YYYY-MM-DD`` strings."""
    y1, m1, d1 = (int(part) for part in check_in.split("-"))
    y2, m2, d2 = (int(part) for part in check_out.split("-"))
    return (date(y2, m2, d2) - date(y1, m1, d1)).days


@dataclass(frozen=True)
class Hotel:
    """One hotel. Owns the nightly rate every stay price derives from."""

    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float

    @classmethod
    def from_row(cls, row) -> "Hotel":
        return cls(
            hotel_id=row["hotel_id"],
            hotel_name=row["hotel_name"],
            city=row["city"],
            state=row["state"],
            nightly_rate_usd=float(row["nightly_rate_usd"]),
        )

    def to_dict(self) -> dict:
        return {
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel_name,
            "city": self.city,
            "state": self.state,
            "nightly_rate_usd": self.nightly_rate_usd,
        }


@dataclass(frozen=True)
class Trip:
    """One offered hotel stay with fixed dates, owned by one Hotel."""

    trip_id: str
    hotel_id: str
    trip_name: str
    check_in: str
    check_out: str

    @classmethod
    def from_row(cls, row) -> "Trip":
        return cls(
            trip_id=row["trip_id"],
            hotel_id=row["hotel_id"],
            trip_name=row["trip_name"],
            check_in=row["check_in"],
            check_out=row["check_out"],
        )

    @property
    def nights(self) -> int:
        return _nights_between(self.check_in, self.check_out)


@dataclass(frozen=True)
class User:
    """A demo traveler. One traveler can hold several bookings."""

    user_id: str
    display_name: str

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(user_id=row["user_id"], display_name=row["display_name"])

    def to_dict(self) -> dict:
        return {"user_id": self.user_id, "display_name": self.display_name}


@dataclass(frozen=True)
class Booking:
    """A booking connects one traveler (User) to one offered stay (Trip).

    ``status`` is the field the Update action changes: cancelling a
    booking sets it to ``CANCELLED`` and keeps the record, which is
    what the assignment asks for.
    """

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    VALID_STATUSES = (CONFIRMED, CANCELLED)

    booking_id: str
    user_id: str
    trip_id: str
    booked_on: str
    status: str

    @classmethod
    def from_row(cls, row) -> "Booking":
        return cls(
            booking_id=row["booking_id"],
            user_id=row["user_id"],
            trip_id=row["trip_id"],
            booked_on=row["booked_on"],
            status=row["status"],
        )

    def to_dict(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "trip_id": self.trip_id,
            "booked_on": self.booked_on,
            "status": self.status,
        }


@dataclass(frozen=True)
class StayOffer:
    """A Trip joined to its Hotel through ``hotel_id``.

    This is the record the search view renders: it resolves the
    one-to-many Hotel -> Trip relationship and adds the two derived
    values (nights and stay price) the table displays.
    """

    trip: Trip
    hotel: Hotel

    @property
    def nights(self) -> int:
        return self.trip.nights

    @property
    def stay_price_usd(self) -> float:
        return round(self.nights * self.hotel.nightly_rate_usd, 2)

    def to_dict(self) -> dict:
        return {
            "trip_id": self.trip.trip_id,
            "trip_name": self.trip.trip_name,
            "hotel_id": self.hotel.hotel_id,
            "hotel_name": self.hotel.hotel_name,
            "city": self.hotel.city,
            "state": self.hotel.state,
            "check_in": self.trip.check_in,
            "check_out": self.trip.check_out,
            "nights": self.nights,
            "nightly_rate_usd": self.hotel.nightly_rate_usd,
            "stay_price_usd": self.stay_price_usd,
        }


@dataclass(frozen=True)
class BookingRecord:
    """A Booking joined to the traveler and the stay it points at.

    Booking history needs a readable row, not raw foreign keys, so this
    resolves ``user_id`` and ``trip_id`` into the related records.
    """

    booking: Booking
    user: User
    offer: StayOffer

    def to_dict(self) -> dict:
        return {
            "booking_id": self.booking.booking_id,
            "booked_on": self.booking.booked_on,
            "status": self.booking.status,
            "user_id": self.user.user_id,
            "traveler": self.user.display_name,
            "trip_id": self.offer.trip.trip_id,
            "trip_name": self.offer.trip.trip_name,
            "hotel_name": self.offer.hotel.hotel_name,
            "city": self.offer.hotel.city,
            "state": self.offer.hotel.state,
            "check_in": self.offer.trip.check_in,
            "check_out": self.offer.trip.check_out,
            "nights": self.offer.nights,
            "stay_price_usd": self.offer.stay_price_usd,
        }
