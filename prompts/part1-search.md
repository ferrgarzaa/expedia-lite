# Selected Prompts — Part 1 (City Search)

## Backend data + search logic

Create framework-free functions in `backend/app/data.py` that:
- read `hotels.csv` and `trips.csv` with `encoding="utf-8-sig"`;
- join a trip to its hotel by `hotel_id`;
- search trips by city, case-insensitive;
- derive nights from check-in/check-out and stay price from
  nights × nightly rate.
Do not add FastAPI code in this file.

## FastAPI path

Expose `GET /api/search?city=...` in `backend/app/main.py` that
calls `search_trips_by_city` and returns `{query, count, results}`
as JSON. Add CORS for `http://localhost:5173` only. Keep join logic
in `data.py`.

## Backend tests

Add a pytest suite covering the city/trip-ID pairs from the sample
data README's "Concrete records to check" table, including the
Miami (no-match) case.

## Frontend search UI

Build a Vue component with a labeled city input, a Search button, a
results table, and a distinct "no results" message. Fetch from
`/api/search`. No blue buttons. Keep the fetch call separate from
presentation markup.
