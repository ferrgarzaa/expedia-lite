# Design note — Expedia Lite

How the application is decomposed, and why each layer owns what it
owns. This note covers both parts of Assignment 1; Part 2 added the
SQLite storage and the Model–View–Controller split.

## The four layers

### Model — `backend/app/models.py`

The Model holds the data and the relationships. Each record type is a
frozen dataclass built from a database row:

```
Hotel  1 ─── *  Trip        Trip.hotel_id  → Hotel.hotel_id
Trip   1 ─── *  Booking     Booking.trip_id → Trip.trip_id
User   1 ─── *  Booking     Booking.user_id → User.user_id
```

Two composite models resolve those relationships for the interface:

- `StayOffer` — a `Trip` joined to its `Hotel`, plus the two derived
  values the results table shows (`nights`, `stay_price_usd`).
- `BookingRecord` — a `Booking` joined to the traveler who made it and
  the stay it points at, so history shows names instead of foreign keys.

`Booking` also owns the status vocabulary (`confirmed`, `cancelled`),
which is what makes "cancel" an update rather than a delete.

The Model knows nothing about SQLite, FastAPI, or Vue. It can be
imported and tested on its own.

### View — `frontend/`

The View is the Vue 3 application. It owns everything the traveler
sees and does:

- `App.vue` — the shell: brand header, the two tabs, and the signal
  that tells booking history to reload after a booking is created.
- `components/TripSearch.vue` — hotel-name input, Search button,
  results table, the "no results" message, and the inline booking form.
- `components/BookingHistory.vue` — the history table, status badges,
  Cancel, and Delete with a confirmation step.
- `assets/main.css` — the design tokens shared by both tabs.
- `api.js` — the single place the View talks to the backend. Every call
  is `fetch` against a FastAPI path; the View never sees SQLite, the
  CSVs, or how records are joined.

### Controller — `backend/app/controllers/`

The Controller layer is the only code that runs SQL. It reads rows,
hands them to the Model, and returns Model objects.

- `travel_controller.py` — reads. Hotel-name search (a `JOIN` from
  `trips` to `hotels` on `hotel_id`, matched case-insensitively and
  partially), single stay lookup, and the demo travelers.
- `booking_controller.py` — the database controller for booking CRUD.
  One function per action:

  | Action | Function | What it does |
  | --- | --- | --- |
  | Create | `create_booking` | Validates the traveler and the stay, rejects a duplicate confirmed booking, assigns the next unused `B###` id, inserts the row |
  | Read | `list_bookings`, `get_booking` | Returns history joined to traveler and stay |
  | Update | `update_booking_status`, `cancel_booking` | Sets the status; cancelling keeps the row |
  | Delete | `delete_booking` | Removes exactly that row |

  Rule violations raise `BookingError`; the controller never raises an
  HTTP error, because it does not know HTTP exists.

`backend/app/database.py` sits underneath: connection, schema, and the
one-time seed. It deliberately performs no CRUD, so there is exactly
one place each booking action can happen.

### Communication — `backend/app/main.py` (FastAPI)

FastAPI is the boundary between the View and the backend. Each path
does three things and nothing more: validate the request body with a
Pydantic model, call one controller function, return JSON. A
`BookingError` becomes a `400` (or `404` for a missing booking), which
is how the View gets a message it can show the traveler.

CORS is enabled for `http://127.0.0.1:5173` because the Vue dev server
and FastAPI run on different ports during development.

## Why this split

- **The join lives in one place.** Only `travel_controller` knows that a
  stay's hotel is found through `hotel_id`. Changing the query does not
  touch FastAPI or Vue.
- **Each CRUD action has one entry point.** The interface cannot cancel
  a booking by a different route than the tests do, so what the tests
  prove is what the traveler gets.
- **Storage is swappable.** Part 1 read CSVs; Part 2 reads SQLite. The
  View did not need to know, because both were reached through the same
  FastAPI paths.

## Seeding and persistence

`seed_if_empty()` checks the `hotels` table before inserting anything
and returns `False` when it is already populated. Startup therefore:

1. creates the tables if missing (`CREATE TABLE IF NOT EXISTS`),
2. seeds the four supplied CSVs only on a genuinely empty database,
3. leaves every later change alone.

That is what makes additions, cancellations, and deletions survive a
browser refresh and a restart of both servers without the starter
records duplicating or reappearing.
