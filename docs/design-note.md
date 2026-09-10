# Design Note — Expedia Lite (Part 1)

## Layers

- **Interface (Vue, `frontend/`)**: a city text input, a Search
  button, a results table, and a distinct "no results" message.
  Owns only presentation and the fetch call — no data logic.
- **Logic / API (FastAPI, `backend/app/main.py`)**: exposes
  `GET /api/search?city=...`, calls the data layer, and serializes
  the response as JSON. Handles CORS for local development.
- **Data (`backend/app/data.py`)**: framework-free Python. Reads
  `hotels.csv` and `trips.csv`, joins a trip to its hotel by
  `hotel_id`, and derives nights and stay price from the check-in/
  check-out dates and nightly rate.
- **Persistence (Part 1)**: the CSV files themselves — read-only for
  this part. Part 2 will move persistence to SQLite.

## Why this split

City search is a decision (case-insensitive match, empty-result
handling) that belongs in the logic layer, not the interface. The
interface never parses CSVs or knows about `hotel_id` — it only
reads the JSON fields the API already joined.

## Part 2 preview

SQLite will replace the CSVs as the source of truth after an initial
seed. FastAPI will gain `POST /api/bookings` (create), the existing
search response already supports read, `PATCH` for status updates
(cancel), and `DELETE` for removing a test booking. The frontend
gains a booking action and a history view; the search UI is
unchanged.
