# Expedia Lite — Part 2

## Repository and commit

https://github.com/ferrgarzaa/expedia-lite at commit `e434fcf845d18dd4a91513da6b349a4144d30695`

## Implementation

Since Part 1, the backend's persistence moved from reading CSVs directly to a SQLite database (`backend/data/expedia_lite.db`). `backend/app/db.py` owns the schema, a one-time seed from the sample CSVs (`seed_if_empty` checks if the `hotels` table is already populated before inserting, so restarting the app never duplicates or reloads the starter records), the city search join, and full booking CRUD (create, list for history, update status to cancel, delete). `backend/app/main.py` exposes this through `GET /api/users`, `GET /api/bookings`, `POST /api/bookings`, `PATCH /api/bookings/{id}`, and `DELETE /api/bookings/{id}`, running `init_db` + `seed_if_empty` once on startup. The Vue frontend now has two tabs: `TripSearch.vue` (search plus an inline "Book" form per result) and the new `BookingHistory.vue` (history table with Cancel and Delete actions), both talking to the backend only through `fetch`.

## Verification

| Action | Expected | Observed |
| --- | --- | --- |
| `pytest` | 16 passed | 16 passed |
| `npm run lint` | 0 errors | 0 errors |
| `npm run build` | Build succeeds | Build succeeds |
| Create a booking through the interface | Confirmation message with a new booking ID | "Booked! Confirmation B007. Check the Booking History tab." |
| New booking appears in history | Row shows up with status "Confirmed" | Row appeared correctly |
| Cancel the new booking | Status changes to "Cancelled", record stays | "Booking B007 cancelled.", row remained with status Cancelled |
| Delete the new booking | Row disappears, other bookings unaffected | "Booking B007 deleted.", B001 and other seeded bookings still present |
| Restart backend and frontend | Seeded data and prior changes persist, no duplication | Confirmed via automated restart test and manual restart |

![Booking created](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/booking-created.png)

![Booking appears in history](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/booking-in-history.png)

![Booking cancelled](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/booking-cancelled.png)

![Booking deleted](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/booking-deleted.png)

## Project context and next steps

- README: https://github.com/ferrgarzaa/expedia-lite/blob/main/README.md
- AGENTS.md: https://github.com/ferrgarzaa/expedia-lite/blob/main/AGENTS.md
- Design note: https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/design-note.md
- Selected prompts: https://github.com/ferrgarzaa/expedia-lite/blob/main/prompts/part2-crud.md
- Current handoff: https://github.com/ferrgarzaa/expedia-lite/blob/main/handoffs/current.md

Remaining limitations: no authentication (travelers are chosen from a dropdown of seeded demo users); deleting the SQLite file resets the app to the seeded starter data on the next run (expected behavior). This completes both parts of Assignment 1.

## Repository and commit

https://github.com/ferrgarzaa/expedia-lite at commit `09efad52247680bd90789f204b2bba2cef2bbc85`

## Implementation

The backend (`backend/app/data.py`) reads `hotels.csv` and `trips.csv`, joins each trip to its hotel by `hotel_id`, and computes the number of nights and estimated stay price from the check-in/check-out dates and the hotel's nightly rate. FastAPI (`backend/app/main.py`) exposes this as `GET /api/search?city=...` and returns JSON; it contains no join logic itself. The Vue frontend (`frontend/src/components/TripSearch.vue`) owns the city input, Search button, results table, and a distinct "no results" message, and talks to the backend only through `fetch`.

## Verification

| Action | Expected | Observed |
| --- | --- | --- |
| Search "Boston" | 4 rows (T001, T002, T009, T010) | 4 rows returned, matching hotel names, dates, and prices |
| Search "Miami" | "No hotel stays found for..." message | Message displayed correctly, no table shown |
| `pytest` | 5 passed | 5 passed |
| `npm run lint` | 0 errors | 0 errors |
| `npm run build` | Build succeeds | Build succeeds |

![Boston search results](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/boston.webp)

![Miami no-results message](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/screenshots/miami.webp)

## Project context and next steps

- README: https://github.com/ferrgarzaa/expedia-lite/blob/main/README.md
- AGENTS.md: https://github.com/ferrgarzaa/expedia-lite/blob/main/AGENTS.md
- Design note: https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/design-note.md
- Selected prompts: https://github.com/ferrgarzaa/expedia-lite/blob/main/prompts/part1-search.md
- Current handoff: https://github.com/ferrgarzaa/expedia-lite/blob/main/handoffs/current.md

Remaining limitations: city search requires the full city name (no partial matching yet); no persistence layer yet (CSVs are read-only in Part 1). Next task: seed SQLite for Part 2 and add booking create/read/update(cancel)/delete through the frontend.