# Expedia Lite — Part 2

## Repository and commit

https://github.com/ferrgarzaa/expedia-lite at commit `2059c2db2f6da8be10f432300dd5cff21bf300c8`

Part 2 was developed on the feature branch `part2-hotel-search-mvc`, reviewed
and checked, then merged into `main`; the commit above is the merged
final commit on `main`. The Part 1 checkpoint is preserved at commit
`09efad52247680bd90789f204b2bba2cef2bbc85`.

## Implementation

Expedia Lite is a Vue frontend, a Python backend, and FastAPI between
them, in separate `frontend/` and `backend/` folders.

**Part 1** read `hotels.csv` and `trips.csv`, joined each trip to its
hotel by `hotel_id`, and returned the matching stays as JSON for a
search form and results table.

**Part 2 changed four things.**

*Storage moved to SQLite.* `backend/app/database.py` owns the
connection, the schema for `hotels`, `trips`, `users`, and `bookings`,
and a one-time seed from the four supplied CSVs into
`backend/data/expedia_lite.db`. `seed_if_empty()` checks whether the
`hotels` table already holds rows and returns without touching anything
if it does, so restarting the app never duplicates or reloads the
starter records. After seeding, every read and write goes to SQLite, and
travelers can add bookings beyond the seeded examples. Supplied ids are
preserved and new bookings continue the `B###` sequence without reusing
one.

*The backend was restructured into Model–View–Controller.*
`backend/app/models.py` is the **Model**: `Hotel`, `Trip`, `User`, and
`Booking` hold the records and the relationships between them
(`Trip.hotel_id → Hotel`, `Booking.trip_id → Trip`,
`Booking.user_id → User`), plus two joined views, `StayOffer` and
`BookingRecord`, that resolve those relationships for the interface.
`backend/app/controllers/` is the **Controller** layer and the only code
that runs SQL: `travel_controller.py` reads hotels, stays, and
travelers, and `booking_controller.py` is the database controller that
performs booking CRUD — `create_booking`, `list_bookings`/`get_booking`,
`update_booking_status`/`cancel_booking`, and `delete_booking`. The Vue
frontend is the **View**. `backend/app/main.py` stays a thin FastAPI
layer that validates a request, calls one controller function, and
returns JSON; it holds no search, join, or CRUD logic and never touches
SQLite. It exposes `GET /api/search`, `GET /api/stays`, `GET /api/users`,
`GET /api/bookings`, `POST /api/bookings`, `PATCH /api/bookings/{id}`,
and `DELETE /api/bookings/{id}`.

*Search now takes a hotel name.* Part 1 searched by city; the form,
the FastAPI path (`GET /api/search?hotel=...`), and the controller query
now match on hotel name, case-insensitively and on part of a name, with
the same distinct "no results" message.

*The interface gained booking and history, and was rebuilt using the UI
research approach from In-class Activity 2.* `App.vue` is a shell with
two tabs. `TripSearch.vue` owns the hotel-name input, the results table,
and an inline booking form on each row. `BookingHistory.vue` owns the
history table with Cancel and Delete. All four CRUD actions are
performed through the frontend, which talks to the backend only through
`frontend/src/api.js`. The UI work applied one set of design tokens in
`assets/main.css` so both tabs read as one product; one clear primary
action per view, with the destructive action outlined in red and behind
a confirmation step; a visible message after every action, including the
reason a booking was rejected; explicit loading, empty, and no-results
states instead of a blank screen; and status shown as a labelled badge
(`Confirmed` / `Cancelled`) rather than colour alone, with visible focus
rings and scoped table headers for screen readers.

## Verification

Changes were scanned file by file in VS Code before committing.

| Action | Expected | Observed |
| --- | --- | --- |
| `pytest` | All pass | 23 passed |
| `npm run lint` | 0 errors | 0 errors |
| `npm run build` | Build succeeds | Build succeeded, 18 modules transformed |
| Search `Harbor Lantern Hotel` | Matching stays in a labelled table | 2 rows (`T001`, `T009`) with hotel, location, dates, nights, rate, and stay price |
| Search `Hotel Miami` | Clear no-results message, no table | "No hotel stays found for “Hotel Miami”. Check the spelling or try part of the name." |
| **Create** — book `Boston Autumn Weekend` as Demo Traveler 2 | Confirmation with a new booking id | "Booked! Confirmation B007 for Demo Traveler 2 at Harbor Lantern Hotel." |
| **Read** — open Booking history | New booking listed as Confirmed | 7 rows; `B007` present with badge Confirmed |
| Refresh the browser, reopen history | `B007` still present | `B007` still present after refresh |
| **Update** — cancel `B007` | Status Cancelled, record retained | "Booking B007 cancelled. The record stays in your history."; badge Cancelled, row still in the table |
| **Delete** — delete `B007` | Row removed, other records untouched | "Booking B007 deleted permanently."; `B007` gone, `B001` and the other seeded bookings still present, back to 6 rows |
| Restart backend and frontend | Post-seed changes persist, starter records not duplicated or reloaded | A booking added after seeding, a cancellation of `B001`, and a deletion of `B003` all survived the restart; 12 stays, no duplicate rows |

Every check matched its expected result. Full detail, including the
commands used for the restart check, is in
[docs/verification.md](https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/verification.md).

**Search by hotel name**

![Hotel-name search results](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/02-search-results.png)

**No results**

![No-results message](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/03-no-results.png)

**Create**

![Booking created](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/05-booking-created.png)

**Read**

![Booking appears in history](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/06-booking-in-history.png)

**Persists after a browser refresh**

![Booking still present after refresh](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/07-after-refresh.png)

**Update (cancel, record retained)**

![Booking cancelled](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/08-booking-cancelled.png)

**Delete**

![Booking deleted](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/10-booking-deleted.png)

## Demo video

A demo under three minutes showing a traveler searching for a hotel,
booking a stay, reading it back in history, cancelling it, and deleting
it:

REPLACE_WITH_VIDEO_LINK

## Project context and next steps

- README: https://github.com/ferrgarzaa/expedia-lite/blob/main/README.md
- AGENTS.md: https://github.com/ferrgarzaa/expedia-lite/blob/main/AGENTS.md
- Design note: https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/design-note.md
- Selected prompts: https://github.com/ferrgarzaa/expedia-lite/blob/main/prompts/part2-crud.md
- Current handoff: https://github.com/ferrgarzaa/expedia-lite/blob/main/handoffs/current.md

Remaining limitations: there is no authentication, so the traveler is
chosen from a dropdown of the seeded demo users and anyone using the app
can act as any traveler; the optional bonus (demo authentication and
surge pricing) was not attempted, so the stay price is always
`nights × nightly_rate_usd`; the app does not model room inventory, so a
stay can be booked by an unlimited number of travelers; and deleting
`backend/data/expedia_lite.db` resets the app to the seeded starter data
on the next run, which is expected behaviour.

Next task: Assignment 1 is complete. If the project continues, the next
step is the optional bonus — demo user authentication so booking history
is scoped to the signed-in traveler, followed by surge-pricing logic in a
pricing module that `travel_controller` calls when building a
`StayOffer`.
