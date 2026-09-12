# Agent Working Rules — Expedia Lite

Durable instructions for any agent (human or AI) working on this
project. Read this and `README.md` before making changes.

## Project rules

- Keep frontend and backend responsibilities separate. The frontend
  never reads CSV/SQLite data directly; it only calls the FastAPI
  JSON endpoints.
- Do not add dependencies without approval. Follow CHECK → TAKE
  ACTION → VERIFY before installing anything.
- Do not use blue buttons.
- Keep changes within the requested scope.
- When tests exist, run them before reporting completion
  (`backend/.venv/bin/pytest`, `npm run lint`, `npm run build`).
- Report every file changed and any check that was not run.
- Preserve existing record IDs (`hotel_id`, `trip_id`, `user_id`,
  `booking_id`); assign new unique IDs to new records.
- For Part 2: seed SQLite once. Restarting the app must not
  duplicate or reset the starter records, and must preserve any
  bookings added, updated, or deleted through the app.

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
5. Verify `GET /api/search?city=Boston` returns 4 trips
   (T001, T002, T009, T010) and `GET /api/search?city=Miami`
   returns 0.
6. Through the visible interface, search "Boston" and confirm the
   results table shows 4 rows; search "Miami" and confirm the
   no-results message appears.
7. Create a booking through the interface, confirm it appears in
   Booking History, cancel it (record stays, status changes), then
   delete it (row disappears).
8. Restart the backend and frontend against the same database file
   and confirm the seeded rows appear exactly once and no prior
   change was lost.
9. Stop only the processes created by this smoke test.
10. Report concise evidence: tests, static checks, API responses, UI
    behavior, and cleanup.

## COMBINED TRIGGER

"AutoLoop: run the smoke test" — run the SmokeTest macro; if an
in-scope check fails, apply the AutoLoop rules and repeat until it
passes, five cycles are exhausted, or a stopping condition is
reached.
