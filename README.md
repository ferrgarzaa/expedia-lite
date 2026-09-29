# Expedia Lite

A small local travel application built for IST 402 Assignments 1 and 2.

- **Assignment 2 · Part 1** — live hotel search by U.S. ZIP code
  (Geoapify through FastAPI) shown as a synchronized list and Leaflet map.
  See [docs/part1/](docs/part1/).

- **Part 1** — search hotel stays by hotel name.
- **Part 2** — the same search backed by SQLite, plus simulated booking
  and booking history with full create / read / update / delete through
  the interface.

## Architecture

The backend follows the **Model–View–Controller** split discussed in
class.

| Layer | Where it lives | What it owns |
| --- | --- | --- |
| **Model** | `backend/app/models.py` | The records and the relationships between them: `Hotel`, `Trip`, `User`, `Booking`, plus the joined `StayOffer` and `BookingRecord` views. Plain Python; no SQL, no HTTP. |
| **View** | `frontend/` (Vue 3) | The interface: search form, results table, booking form, booking history, status badges, and every message the traveler reads. Talks to the backend only through `frontend/src/api.js`. |
| **Controller** | `backend/app/controllers/` | The only code that touches SQLite. `travel_controller.py` reads hotels, stays, and travelers; `booking_controller.py` performs booking CRUD. |
| Storage | `backend/app/database.py` | Connection, schema, and the one-time seed from the sample CSVs. No CRUD of its own. |
| Communication | `backend/app/main.py` (FastAPI) | HTTP paths only. Receives requests, calls a controller, returns JSON. Contains no search, join, or CRUD logic. |

```
Vue view  ──fetch JSON──▶  FastAPI paths  ──▶  controllers  ──▶  SQLite
                                                    │
                                                    ▼
                                                  models
```

### Data and seeding

`backend/data/` holds the supplied sample CSVs (`hotels.csv`,
`trips.csv`, `users.csv`, `bookings.csv`) and the SQLite file
`expedia_lite.db`, which is created on first run.

On startup the app runs `init_db()` and then `seed_if_empty()`.
`seed_if_empty` checks whether the `hotels` table already holds rows and
returns immediately if it does, so:

- the starter records are inserted exactly once;
- restarting the backend never duplicates or reloads them;
- bookings added, cancelled, or deleted through the interface survive a
  browser refresh and a full restart of both servers.

The CSVs are the *initial* data, not a limit: new bookings are stored in
SQLite with fresh `B###` ids that never collide with the seeded ones.

### API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/search?hotel=<name>` | Search offered stays by hotel name |
| `GET` | `/api/stays` | Every offered stay |
| `GET` | `/api/users` | Demo travelers for the booking form |
| `GET` | `/api/bookings` | **Read** — booking history |
| `POST` | `/api/bookings` | **Create** — book a stay |
| `PATCH` | `/api/bookings/{id}` | **Update** — cancel (record retained) |
| `DELETE` | `/api/bookings/{id}` | **Delete** — remove the record |
| `GET` | `/api/hotels/nearby?zip=<5 digits>` | Live hotels ≤ 5 km from the Geoapify location of a U.S. ZIP. Errors: 422 `invalid_zip`, 404 `zip_not_found`, 503 `rate_limited`/`missing_api_key`, 502 provider failure |

### Live hotel search (Assignment 2)

```
Vue (HotelDiscovery + HotelMap) ─▶ FastAPI /api/hotels/nearby
   ─▶ controllers/hotel_discovery_controller.py (validate, verify ZIP, parse)
   ─▶ services/geoapify_client.py (only code that calls Geoapify; holds the key)
   ─▶ models.SearchCenter / models.ExternalHotel (no price field)
```

## Requirements

- Python 3.10+
- Node.js 20+ and npm

## Setup and run

### Backend

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env        # then paste your Geoapify key into backend/.env
./.venv/bin/pytest                                   # run tests
./.venv/bin/uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://127.0.0.1:8000`; interactive docs at
`http://127.0.0.1:8000/docs`.

**Geoapify key:** create a free account at https://myprojects.geoapify.com,
create a project, copy its API key into `backend/.env` as
`GEOAPIFY_API_KEY=...`. The file is git-ignored; never commit it and never
put the key in `frontend/`. The map tiles come from OpenStreetMap and need
no key.

**Offline sample mode** (no key, no quota — labeled fixture data only):
`./.venv/bin/python scripts/run_with_samples.py` (ZIPs: 16802 results,
00000 not found, 99999 no hotels, 50000 failure, 42900 rate limit).

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run build          # production build check
npm run dev -- --port 5173
```

Frontend runs at `http://127.0.0.1:5173`. Type a hotel name (for example
`Harbor Lantern Hotel`), click **Search**, then **Book** a stay and open
the **Booking history** tab to cancel or delete it.

## Interface

The Part 2 interface applies the UI research approach from In-class
Activity 2:

- one set of design tokens in `frontend/src/assets/main.css`, so both
  tabs read as one product;
- one clear primary action per view, with destructive actions outlined
  in red and behind a confirmation step;
- every action answered by a visible message (created, cancelled,
  deleted, or the reason it failed);
- explicit loading, empty, and no-results states instead of a blank
  screen;
- status shown as a labelled badge (`Confirmed` / `Cancelled`) rather
  than colour alone, with visible focus rings and table headers scoped
  for screen readers.

## Current implementation status

- [x] Part 1: hotel-name search over hotels and trips joined by
      `hotel_id`, returned as JSON and rendered in a results table.
- [x] Clear "no results" message for a hotel name with no matches.
- [x] Part 2: SQLite seeded once; booking create, read, update (cancel),
      and delete performed through the frontend.
- [x] Changes persist across a browser refresh and a restart of both
      servers, with no duplicated starter records.

## Known limitations

- No authentication; travelers are chosen from a dropdown of the seeded
  demo users (the optional bonus was not attempted).
- Surge pricing is not implemented; the stay price is
  `nights × nightly_rate_usd`.
- Deleting `backend/data/expedia_lite.db` resets the app to the seeded
  starter data on the next run. This is expected behaviour.

See `docs/design-note.md` for layer responsibilities,
`docs/verification.md` for the checks that were run, and
`handoffs/current.md` for the latest status and next task.
