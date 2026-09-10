# Handoff — Current Status

## What works

- Backend: `GET /api/search?city=...` reads `hotels.csv` +
  `trips.csv`, joins on `hotel_id`, returns JSON with derived nights
  and stay price. Case-insensitive city match.
- Frontend: city input, Search button, results table, and a distinct
  "no results" message, wired to the backend via `fetch`.

## What was checked

- `pytest`: 5/5 passing, matching the sample-data README's expected
  trip IDs per city (Boston → 4, New York → 3, Philadelphia → 2,
  Washington → 2, State College → 1, Miami → 0).
- `npm run lint`: 0 errors.
- `npm run build`: production build succeeds.
- Manual: backend + frontend started together locally; confirmed
  `GET /api/search?city=Boston` returns the 4 expected trip IDs and
  the frontend dev server responds with HTTP 200.
- Still needed before submission: browser screenshots of a
  successful Boston search and a Miami no-results search, taken by
  the student running the app locally.

## Remaining limitations

- No SQLite persistence yet (Part 1 reads CSVs directly, as
  specified).
- City match requires the full city name, not partial text.

## Next task

- Take browser screenshots for `report.md` (successful search +
  no-results), fill in `docs/verification.md`'s Observed column,
  commit, and push. Identify the exact Part 1 commit hash for the
  report.
- Then start Part 2: seed SQLite from the CSVs and add booking
  create/read/update(cancel)/delete through the frontend.
