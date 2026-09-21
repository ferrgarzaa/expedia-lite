# Handoff — current status

_Last updated: 2026-09-21 (end of Assignment 1, Part 2)._

## What works

- **Search by hotel name.** The Vue form sends the hotel name to
  `GET /api/search?hotel=...`; `travel_controller` joins `trips` to
  `hotels` on `hotel_id` and returns the matching stays with nights and
  stay price. Matching is case-insensitive and accepts part of a name.
  A hotel name with no matches produces a distinct message instead of an
  empty table.
- **SQLite storage.** `database.py` creates the schema and seeds the
  four supplied CSVs exactly once. Every read and write after that goes
  to `backend/data/expedia_lite.db`.
- **Full CRUD through the interface.** Book a stay from the results
  table (create), see it in Booking history (read), cancel it so the
  record stays with status `cancelled` (update), and delete it
  permanently behind a confirmation step (delete).
- **Model–View–Controller.** Records and relationships in
  `app/models.py`; SQL only in `app/controllers/`; Vue owns the
  interface; `main.py` is HTTP-only.
- **Persistence.** Additions, updates, and deletions survive a browser
  refresh and a restart of both servers. Starter records are never
  duplicated or reloaded.

## What was checked

23 backend tests pass, `npm run lint` reports 0 errors, and
`npm run build` succeeds. All eight browser checks in
`docs/verification.md` matched their expected results, including the
restart check. Screenshots are in `docs/screenshots/`.

## Remaining limitations

- No authentication. The traveler is chosen from a dropdown of the
  seeded demo users, so anyone using the app can act as any traveler.
  The optional bonus (demo authentication and surge pricing) was not
  attempted.
- Stay price is always `nights × nightly_rate_usd`; there is no
  seasonal or demand pricing.
- A traveler is blocked from holding two *confirmed* bookings for the
  same stay, but the app does not model room inventory, so a stay can be
  booked by an unlimited number of travelers.
- Deleting `backend/data/expedia_lite.db` resets the app to the seeded
  starter data on the next run. This is expected.

## Next task

Assignment 1 is complete. If the project continues, the next step is the
optional bonus: demo user authentication so booking history is scoped to
the signed-in traveler, followed by surge-pricing logic in a pricing
module that `travel_controller` calls when building a `StayOffer`.
