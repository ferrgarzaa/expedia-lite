# Design Note — Expedia Lite

## Layers

- **Interface (Vue, `frontend/`)**: `TripSearch.vue` owns the city
  input, Search button, results table, "no results" message, and an
  inline booking form (traveler dropdown + confirm). `BookingHistory.vue`
  owns the history table and its Cancel/Delete buttons. Neither
  component knows about SQLite or how a query is built — they only
  call `fetch` and render the JSON they get back.
- **Logic / API (FastAPI, `backend/app/main.py`)**: exposes
  `GET /api/search`, `GET /api/users`, `GET /api/bookings`,
  `POST /api/bookings`, `PATCH /api/bookings/{id}`, and
  `DELETE /api/bookings/{id}`. Opens a connection, calls `db.py`,
  and serializes the result as JSON. Runs `init_db` + `seed_if_empty`
  once at startup.
- **Data (`backend/app/db.py`)**: framework-free SQL. Owns the
  schema, the city-search join, the booking history join, and every
  create/update/delete. Generates new booking IDs by continuing the
  existing `B###` numbering so seeded IDs are never reused.
- **Persistence (`backend/data/expedia_lite.db`)**: a SQLite file.
  `seed_if_empty` checks whether the `hotels` table already has rows
  before inserting the CSV data, so restarting the app — or just
  re-running `init_db` — never duplicates or reloads the starters.

## Why this split

Booking is a decision (assign a new unique ID, default status
`confirmed`, keep the record on cancel) that belongs in the data
layer, not the interface or the API layer. The frontend never
constructs a booking ID or writes SQL; it only sends `{user_id,
trip_id}` and displays whatever the backend returns.

## Changes since Part 1

- Replaced direct CSV reads in the search path with SQLite reads
  (`db.search_trips_by_city`); `data.py`'s CSV loaders are now used
  only for the one-time seed.
- Added `users`, and re-used `bookings`, as SQLite tables seeded
  from `users.csv` and `bookings.csv`.
- Added booking CRUD endpoints and the corresponding UI (booking
  form in search results, a new Booking History tab).
- Added `docs/verification.md` entries and `tests/test_db.py` for
  the new persistence behavior, including a restart test.
