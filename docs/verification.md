# Verification — Expedia Lite

Every check recorded here was run against the submitted code.

## Automated checks

| Check | Command | Expected | Observed |
| --- | --- | --- | --- |
| Backend tests | `pytest` | All pass | 23 passed |
| Frontend lint | `npm run lint` | 0 errors | 0 errors (oxlint + eslint) |
| Frontend build | `npm run build` | Build succeeds | Built in 169 ms, 18 modules transformed |

The suite covers the Model, both controllers, and the FastAPI paths,
including a test that simulates a restart and asserts that seeding does
not run a second time.

## Manual review

Changes were scanned file by file in VS Code before committing:
`backend/app/models.py`, `backend/app/database.py`,
`backend/app/controllers/travel_controller.py`,
`backend/app/controllers/booking_controller.py`,
`backend/app/main.py`, `frontend/src/api.js`, `frontend/src/App.vue`,
`frontend/src/components/TripSearch.vue`,
`frontend/src/components/BookingHistory.vue`, and
`frontend/src/assets/main.css`.

## Browser checks

Backend on `http://127.0.0.1:8000`, frontend on
`http://127.0.0.1:5173`, starting from a database seeded from the
supplied CSVs (6 bookings, `B001`–`B006`).

| # | Action | Expected result | Observed result |
| --- | --- | --- | --- |
| 1 | Search `Harbor Lantern Hotel` | Matching stays in a labelled table | 2 rows (`T001`, `T009`), hotel, location, dates, nights, nightly rate, stay price all shown |
| 2 | Search `Hotel Miami` | Clear no-results message, no table | "No hotel stays found for “Hotel Miami”. Check the spelling or try part of the name." |
| 3 | **Create** — Book `Boston Autumn Weekend` as Demo Traveler 2 | Confirmation with a new booking id | "Booked! Confirmation **B007** for Demo Traveler 2 at Harbor Lantern Hotel." |
| 4 | **Read** — open Booking history | The new booking appears, status Confirmed | 7 rows; `B007` present with badge **Confirmed** |
| 5 | Refresh the browser, reopen history | `B007` still there | `B007` still present after refresh |
| 6 | **Update** — Cancel `B007` | Status becomes Cancelled, record retained | "Booking B007 cancelled. The record stays in your history."; badge **Cancelled**, row still in the table |
| 7 | **Delete** — Delete `B007` and confirm | Row disappears, other records untouched | "Booking B007 deleted permanently."; `B007` gone, `B001` and the other seeded bookings still present, back to 6 rows |
| 8 | Restart backend and frontend, reopen the app | Post-seed changes persist, starter records not duplicated or reloaded | A booking added after seeding, a cancellation of `B001`, and a deletion of `B003` all survived the restart; stays still 12, no duplicate rows |

All eight checks matched their expected results.

## Reproducing check 8

```bash
curl -X POST http://127.0.0.1:8000/api/bookings \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"U006","trip_id":"T011"}'
curl -X PATCH http://127.0.0.1:8000/api/bookings/B001 \
  -H 'Content-Type: application/json' -d '{"status":"cancelled"}'
curl -X DELETE http://127.0.0.1:8000/api/bookings/B003
# stop and restart uvicorn, then:
curl http://127.0.0.1:8000/api/bookings
```

Before restart and after restart returned the same six bookings:
`B001 cancelled`, `B002 cancelled`, `B004 confirmed`, `B005 confirmed`,
`B006 cancelled`, `B007 confirmed`.

## Screenshots

Stored in `docs/screenshots/`:

| File | Shows |
| --- | --- |
| `02-search-results.png` | Hotel-name search with results |
| `03-no-results.png` | No-results message |
| `04-booking-form.png` | Inline booking form |
| `05-booking-created.png` | Create confirmation |
| `06-booking-in-history.png` | New booking read back in history |
| `07-after-refresh.png` | Still present after a browser refresh |
| `08-booking-cancelled.png` | Update — cancelled, record retained |
| `09-delete-confirm.png` | Delete confirmation step |
| `10-booking-deleted.png` | Deleted, other records intact |
