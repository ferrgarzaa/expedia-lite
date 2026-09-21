"""FastAPI paths for Expedia Lite.

This module owns HTTP concerns only. It receives requests from the Vue
view, calls the controllers, and returns JSON. It contains no search,
join, or CRUD logic of its own, and it never touches SQLite directly.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.controllers import booking_controller, travel_controller
from app.controllers.booking_controller import BookingError
from app.database import init_db, seed_if_empty

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create the schema and seed the starter records exactly once."""
    init_db()
    seed_if_empty()
    yield


app = FastAPI(title="Expedia Lite API", lifespan=lifespan)

# Development-time CORS: the Vue dev server runs on a different port
# (5173) than FastAPI (8000), so the browser needs explicit permission
# to call this API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookingCreate(BaseModel):
    user_id: str = Field(min_length=1)
    trip_id: str = Field(min_length=1)


class BookingStatusUpdate(BaseModel):
    status: str = Field(min_length=1)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/search")
def search(hotel: str = Query(..., min_length=1)) -> dict:
    """Search offered stays by hotel name.

    Returns a results list (possibly empty) and the query that was
    searched, so the frontend can build a clear "no results" message.
    """
    offers = travel_controller.search_stays_by_hotel_name(hotel)
    return {
        "query": hotel,
        "count": len(offers),
        "results": [offer.to_dict() for offer in offers],
    }


@app.get("/api/stays")
def stays() -> dict:
    offers = travel_controller.list_stays()
    return {"count": len(offers), "results": [o.to_dict() for o in offers]}


@app.get("/api/users")
def users() -> dict:
    """Demo travelers, used to populate the booking form."""
    people = travel_controller.list_users()
    return {"count": len(people), "results": [u.to_dict() for u in people]}


@app.get("/api/bookings")
def read_bookings(user_id: str | None = None) -> dict:
    """READ: booking history, optionally filtered to one traveler."""
    records = booking_controller.list_bookings(user_id)
    return {"count": len(records), "results": [r.to_dict() for r in records]}


@app.post("/api/bookings", status_code=201)
def create_booking(payload: BookingCreate) -> dict:
    """CREATE: book an offered stay for a demo traveler."""
    try:
        record = booking_controller.create_booking(
            payload.user_id, payload.trip_id
        )
    except BookingError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return record.to_dict()


@app.patch("/api/bookings/{booking_id}")
def update_booking(booking_id: str, payload: BookingStatusUpdate) -> dict:
    """UPDATE: change a booking's status (cancel keeps the record)."""
    try:
        record = booking_controller.update_booking_status(
            booking_id, payload.status
        )
    except BookingError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return record.to_dict()


@app.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: str) -> dict:
    """DELETE: remove a booking row completely."""
    try:
        booking_controller.delete_booking(booking_id)
    except BookingError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"deleted": booking_id}
