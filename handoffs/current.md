# Handoff — Current Status

## What works

- Part 1: city search over `hotels.csv` + `trips.csv` (now backed by
  SQLite instead of reading the CSVs directly on every request).
- Part 2: `GET /api/bookings` (history), `POST /api/bookings`
  (create), `PATCH /api/bookings/{id}` (cancel, keeps the record),
  `DELETE /api/bookings/{id}` (remove a test booking). The database
  seeds itself once from the CSVs on first startup and never
  reseeds or duplicates on later startups.
- Frontend: a "Search & Book" tab (search + inline booking form) and
  a "Booking History" tab (list, cancel, delete), no router
  dependency added.

## What was checked

- `pytest`: 16/16 passing, including a restart simulation that opens
  the same SQLite file twice and confirms no duplicate seeding and
  that a change made in the first "run" is visible in the second.
- `npm run lint`: 0 errors. `npm run build`: production build
  succeeds.
- Manual: ran backend + frontend together; searched Boston (4
  results), created a booking through the UI, confirmed it appeared
  in history, cancelled it (record kept, status changed), deleted it
  (row removed), then stopped and restarted both processes and
  confirmed the seeded data and prior changes were still there with
  no duplicates.
- Still needed before submission: browser screenshots for the Part 2
  verification table (booking created, booking history with a
  cancelled row, deletion) taken by the student running the app
  locally.

## Remaining limitations

- No authentication; travelers are chosen from a dropdown of the
  seeded demo users.
- Deleting the `backend/data/expedia_lite.db` file resets the app to
  the seeded starter data on the next run (expected/by design).

## Next task

- Take browser screenshots for Part 2's `report.md` (booking
  history showing a new booking and a cancelled booking), fill in
  `docs/verification.md`'s Observed column, commit on the feature
  branch, merge into `main`, push, and identify the exact final
  commit for the report.
- Beyond this assignment: could add booking-date validation
  (prevent double-booking the same trip) if extended further.
