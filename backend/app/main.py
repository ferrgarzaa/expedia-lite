"""FastAPI paths for Expedia Lite.

This module owns HTTP concerns only: it receives requests, opens a
SQLite connection, calls the framework-free functions in db.py, and
returns JSON. It contains no search, join, or persistence logic
itself.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import db

app = FastAPI(title="Expedia Lite API")

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


@app.on_event("startup")
def on_startup() -> None:
    """Create tables if needed and seed once. Restarting never duplicates data."""
    conn = db.get_connection()
    try:
        db.init_db(conn)
        db.seed_if_empty(conn)
    finally:
        conn.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/search")
def search(city: str = Query(..., min_length=1)) -> dict:
    """Search trips by hotel city (reads from SQLite)."""
    conn = db.get_connection()
    try:
        results = db.search_trips_by_city(conn, city)
    finally:
        conn.close()
    return {"query": city, "count": len(results), "results": results}


@app.get("/api/users")
def get_users() -> list[dict]:
    conn = db.get_connection()
    try:
        return db.list_users(conn)
    finally:
        conn.close()


@app.get("/api/bookings")
def get_bookings() -> list[dict]:
    """Booking history, joined with traveler and trip/hotel details."""
    conn = db.get_connection()
    try:
        return db.list_bookings(conn)
    finally:
        conn.close()


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


@app.post("/api/bookings", status_code=201)
def post_booking(payload: BookingCreate) -> dict:
    conn = db.get_connection()
    try:
        return db.create_booking(conn, payload.user_id, payload.trip_id)
    finally:
        conn.close()


class BookingStatusUpdate(BaseModel):
    status: str


@app.patch("/api/bookings/{booking_id}")
def patch_booking(booking_id: str, payload: BookingStatusUpdate) -> dict:
    conn = db.get_connection()
    try:
        updated = db.update_booking_status(conn, booking_id, payload.status)
    finally:
        conn.close()
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return updated


@app.delete("/api/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str) -> None:
    conn = db.get_connection()
    try:
        removed = db.delete_booking(conn, booking_id)
    finally:
        conn.close()
    if not removed:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
