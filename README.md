# Expedia Lite

A small local travel application built for ETI 300W Assignment 1.
Part 1 added city search over the sample CSVs. Part 2 adds a SQLite
database (seeded once from those same CSVs), simulated booking, and
booking history with cancel/delete, all performed through the
frontend.

## Architecture

- **`backend/`** — Python + FastAPI.
  - `app/data.py` — framework-free CSV readers, used only to seed
    the database the first time it runs. No FastAPI or SQL code.
  - `app/db.py` — framework-free SQLite layer: schema, one-time
    seeding, city search, and booking create/read/update/delete.
    No FastAPI or HTTP code.
  - `app/main.py` — FastAPI paths only. Opens a connection, calls
    `db.py`, and returns JSON. Handles CORS for the local Vue dev
    server and runs `init_db` + `seed_if_empty` on startup.
  - `data/` — the supplied sample CSVs (seed source) and the
    generated `expedia_lite.db` (git-ignored; created on first run).
  - `tests/` — pytest suite for the CSV join logic (`test_data.py`)
    and the SQLite layer (`test_db.py`), including a restart test
    that confirms seeding never duplicates data.
- **`frontend/`** — Vue 3 + Vite, two tabs (no router dependency):
  - `TripSearch.vue` — city search, results table, and an inline
    "Book" form per row (choose a traveler, confirm).
  - `BookingHistory.vue` — booking history table with Cancel
    (keeps the record, marks it cancelled) and Delete actions.

The two layers communicate through JSON over HTTP; the frontend has
no knowledge of the database file or how the join/seeding works.

## Requirements

- Python 3.9+ (tested on 3.9 and 3.12)
- Node.js 20+ and npm

## Setup and run

### Backend

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pytest              # run tests
./.venv/bin/uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://127.0.0.1:8000`. Interactive docs at
`http://127.0.0.1:8000/docs`. On first startup it creates
`backend/data/expedia_lite.db` and seeds it from the CSVs; every
later startup reuses that file without reseeding.

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run build   # production build check
npm run dev -- --port 5173
```

Frontend runs at `http://127.0.0.1:5173`. Open it in a browser:
search a city on the "Search & Book" tab, or view/cancel/delete
reservations on the "Booking History" tab.

## Current implementation status

- [x] Part 1: city search over `hotels.csv` + `trips.csv`, joined by
      `hotel_id`, returned as JSON and rendered in a results table.
- [x] Clear "no results" message for a city with no matches.
- [x] Part 2: SQLite seeded once from the CSVs; booking
      create/read/update(cancel)/delete performed through the
      frontend; changes and the seeded data both survive a restart
      without duplication.

## Known limitations

- City matching is case-insensitive but requires the full city name
  (no partial/fuzzy matching yet).
- No authentication; `users.csv` travelers are demo identities
  selected from a dropdown, not logged-in accounts.
- Deleting the SQLite file (`backend/data/expedia_lite.db`) resets
  the app back to the seeded starter data on the next startup.

See `docs/design-note.md` for layer responsibilities and
`handoffs/current.md` for the latest status and next task.
