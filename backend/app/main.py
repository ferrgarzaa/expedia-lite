"""FastAPI paths for Expedia Lite.

This module owns HTTP concerns only: it receives requests, calls the
framework-free functions in data.py, and returns JSON. It does not
contain search or join logic itself.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.data import search_trips_by_city

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


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/search")
def search(city: str = Query(..., min_length=1)) -> dict:
    """Search trips by hotel city.

    Returns a results list (possibly empty) and the query that was
    searched, so the frontend can build a clear "no results" message.
    """
    results = search_trips_by_city(city)
    return {"query": city, "count": len(results), "results": results}
