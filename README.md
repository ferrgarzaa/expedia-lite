# Expedia Lite

A small local travel application built for ETI 300W Assignment 1.
Part 1 lets a traveler search hotel stays ("trips") by city. Part 2
will add simulated booking and booking history backed by SQLite.

## Architecture

- **`backend/`** — Python + FastAPI. Owns data access, the city-search
  join between `hotels.csv` and `trips.csv`, and the JSON API.
  - `app/data.py` — framework-free functions that read the CSVs and
    join a trip to its hotel by `hotel_id`. No FastAPI or HTTP code.
  - `app/main.py` — FastAPI paths only. Calls `data.py` and returns
    JSON. Handles CORS for the local Vue dev server.
  - `data/` — the supplied sample CSVs (`hotels.csv`, `trips.csv`,
    `users.csv`, `bookings.csv`).
  - `tests/` — pytest suite for the search logic.
- **`frontend/`** — Vue 3 + Vite. Owns the city input, the Search
  button, the results table, and the "no results" message. Talks to
  the backend only through `fetch` calls to `/api/search`.

The two layers communicate through JSON over HTTP; the frontend has
no knowledge of the CSV files or how the join is performed.

## Requirements

- Python 3.10+
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
`http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run build   # production build check
npm run dev -- --port 5173
```

Frontend runs at `http://127.0.0.1:5173`. Open it in a browser, type
a city (e.g. `Boston`), and click Search.

## Current implementation status

- [x] Part 1: city search over `hotels.csv` + `trips.csv`, joined by
      `hotel_id`, returned as JSON and rendered in a results table.
- [x] Clear "no results" message for a city with no matches.
- [ ] Part 2: SQLite-backed booking, history, cancel, and delete.

## Known limitations

- City matching is case-insensitive but requires the full city name
  (no partial/fuzzy matching yet).
- No authentication; `users.csv` travelers are demo identities only.

See `docs/design-note.md` for layer responsibilities and
`handoffs/current.md` for the latest status and next task.
