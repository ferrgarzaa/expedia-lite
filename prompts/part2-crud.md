# Selected Prompts — Part 2 (SQLite CRUD)

## SQLite schema and one-time seed

In `backend/app/db.py`, create framework-free functions that:
- define a schema for `hotels`, `trips`, `users`, `bookings`
  matching the CSV columns;
- create tables if they do not exist (`init_db`);
- seed from the CSVs only if the `hotels` table is empty
  (`seed_if_empty`), so restarting the app never duplicates or
  reloads the starter records.
Do not add FastAPI code in this file.

## Search over SQLite

Move the city search join from reading CSVs directly to a SQL query
joining `trips` to `hotels`, case-insensitive, preserving the same
response shape used in Part 1.

## Booking CRUD

Add functions to `db.py` for: creating a booking with a new unique
`B###` ID that continues the existing numbering; listing all
bookings joined with traveler and trip/hotel details for history;
updating a booking's status (e.g. to `cancelled`) while keeping the
row; deleting a booking by ID. Preserve existing IDs; never reuse or
renumber them.

## FastAPI endpoints

Expose `GET /api/users`, `GET /api/bookings`, `POST /api/bookings`,
`PATCH /api/bookings/{id}`, `DELETE /api/bookings/{id}` in
`backend/app/main.py`. Run `init_db` + `seed_if_empty` once on
startup. Keep all SQL and join logic in `db.py`.

## Backend tests

Add a pytest suite for `db.py` covering seeding idempotency, search,
create/read/update/delete, and a restart simulation (open the same
DB file twice, confirm no duplicate seeding and that changes persist).

## Frontend booking UI

Add an inline "Book" form to each search result row (traveler
dropdown fetched from `/api/users`, Confirm button) and a new
"Booking History" tab/component with a table plus Cancel and Delete
actions per row, wired to the new endpoints. No router dependency;
switch tabs with local component state. No blue buttons.
