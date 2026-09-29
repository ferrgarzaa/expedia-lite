# Agent Working Rules — Expedia Lite

Durable instructions for any agent (human or AI) working on this
project. Read this and `README.md` before making changes.

## Project rules

- Keep frontend and backend responsibilities separate. The frontend
  never reads SQLite or the CSV files directly; it only calls the
  FastAPI JSON endpoints through `frontend/src/api.js`.
- Respect the Model–View–Controller split:
  - records and relationships live in `backend/app/models.py`;
  - **every** SQL statement lives in `backend/app/controllers/`;
  - `backend/app/main.py` handles HTTP only — no SQL, no join logic;
  - `backend/app/database.py` owns connection, schema, and seeding, and
    performs no CRUD.
- External APIs (Assignment 2): only `backend/app/services/` calls
  Geoapify. Controllers interpret results; `main.py` maps errors to HTTP.
  API keys live only in `backend/.env` (git-ignored) — never in code,
  commits, screenshots, or `frontend/`.
- Never invent provider data: no prices, ratings, availability, or
  booking confirmations for Geoapify places. Missing fields stay `null`
  and get an honest label in the View.
- A failed provider request must never be shown as an empty search.
- Tests must use the labeled fixtures in `backend/tests/fixtures/`, not
  the live API, and must not depend on a live result count.
- Do not add dependencies without approval. Follow CHECK → TAKE
  ACTION → VERIFY before installing anything: CHECK what is already
  installed (`package.json`, `requirements.txt`); explain the exact
  command and wait for the student's approval; then VERIFY with the
  checks below. (Example: `leaflet@1.9.4` was approved on 2026-09-29.)
- Do not use blue buttons.
- Keep changes within the requested scope.
- Run the checks before reporting completion (`backend/.venv/bin/pytest`,
  `npm run lint`, `npm run build`).
- Report every file changed and any check that was not run.
- Preserve existing record IDs (`hotel_id`, `trip_id`, `user_id`,
  `booking_id`); assign new unique IDs to new records.
- Seed SQLite once. Restarting the app must not duplicate or reset the
  starter records, and must preserve any bookings added, updated, or
  deleted through the app.

## AUTOLOOP MACRO

Trigger: "AutoLoop"

1. Read `AGENTS.md`, `README.md`, and `docs/verification.md`.
2. State the acceptance check for the current task.
3. Run the smallest relevant check.
4. If it fails for an in-scope reason, inspect the evidence, make the
   smallest relevant correction, and rerun the check.
5. Repeat for no more than five correction cycles.
6. Stop early and ask for direction if the next action needs a
   dependency change, destructive action, or broader scope.
7. Report every cycle, the final evidence, and anything not verified.

## SMOKETEST MACRO

Trigger: "Run the smoke test"

1. Read `AGENTS.md`, `README.md`, and `docs/verification.md`.
2. Run the backend pytest suite.
3. Run the frontend lint and production build.
4. Start only the backend (port 8000) and frontend (port 5173)
   processes needed for this test.
5. Verify the API:
   - `GET /api/search?hotel=Harbor Lantern Hotel` returns 2 stays
     (`T001`, `T009`);
   - `GET /api/search?hotel=Hotel Miami` returns 0;
   - `GET /api/bookings` returns the seeded history.
6. Through the visible interface:
   - search a hotel name and confirm the results table;
   - search a hotel name with no matches and confirm the message;
   - **create** a booking and confirm the confirmation message;
   - **read** it in Booking history;
   - **update** it by cancelling and confirm the record is retained
     with status Cancelled;
   - **delete** it and confirm other bookings are untouched.
7. Refresh the browser and restart both servers; confirm the changes
   persist and the starter records are not duplicated or reloaded.
8. Stop only the processes created by this smoke test.
9. Report concise evidence: tests, static checks, API responses, UI
   behavior, persistence, and cleanup.

## COMBINED TRIGGER

"AutoLoop: run the smoke test" — run the SmokeTest macro; if an
in-scope check fails, apply the AutoLoop rules and repeat until it
passes, five cycles are exhausted, or a stopping condition is
reached.
