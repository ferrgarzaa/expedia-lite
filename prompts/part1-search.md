# Selected Prompts — Part 1 (Hotel Search)

## Backend data + search logic

Create framework-free functions that:
- read `hotels.csv` and `trips.csv` with `encoding="utf-8-sig"`;
- join a trip to its hotel by `hotel_id`;
- search stays by hotel name, case-insensitive;
- derive nights from check-in/check-out and stay price from
  nights × nightly rate.
Do not add FastAPI code in this file.

## FastAPI path

Expose `GET /api/search?hotel=...` in `backend/app/main.py` that calls
the search function and returns `{query, count, results}` as JSON. Add
CORS for `http://localhost:5173` only. Keep the join logic out of
`main.py`.

## Backend tests

Add a pytest suite covering the hotel/trip-ID pairs from the sample
data README's "Concrete records to check" table, including a hotel name
with no matches.

## Frontend search UI

Build a Vue component with a labeled hotel-name input, a Search button,
a results table, and a distinct "no results" message. Fetch from
`/api/search`. No blue buttons. Keep the fetch call separate from
presentation markup.

> Note: Part 1 was originally built as a **city** search. When the
> requirement changed to a **hotel name**, the search input, the FastAPI
> path, and the controller query were updated accordingly in Part 2, and
> the tests were rewritten against hotel names. See
> `prompts/part2-crud.md`, prompt 3.
