# Expedia Lite — Part 1

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