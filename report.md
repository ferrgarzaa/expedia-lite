# Expedia Lite — Part 1

## Repository and commit

[Paste your GitHub repository URL and the exact commit hash you are
submitting for Part 1 here, e.g. https://github.com/USERNAME/expedia-lite
at commit `abc1234`.]

## Implementation

The backend (`backend/app/data.py`) reads `hotels.csv` and
`trips.csv`, joins each trip to its hotel by `hotel_id`, and
computes the number of nights and estimated stay price from the
check-in/check-out dates and the hotel's nightly rate. FastAPI
(`backend/app/main.py`) exposes this as `GET /api/search?city=...`
and returns JSON; it contains no join logic itself. The Vue frontend
(`frontend/src/components/TripSearch.vue`) owns the city input,
Search button, results table, and a distinct "no results" message,
and talks to the backend only through `fetch`.

## Verification

| Action | Expected | Observed |
| --- | --- | --- |
| Search "Boston" | 4 rows (T001, T002, T009, T010) | [fill in] |
| Search "Miami" | "No hotel stays found for..." message | [fill in] |
| `pytest` | 5 passed | 5 passed |
| `npm run lint` | 0 errors | 0 errors |
| `npm run build` | Build succeeds | Build succeeds |

[Embed or link screenshots stored in the repository, e.g.
`![Boston search results](docs/screenshots/boston-search.png)`]

## Project context and next steps

- README: [link to README.md in your repo]
- AGENTS.md: [link to AGENTS.md in your repo]
- Design note: [link to docs/design-note.md in your repo]
- Selected prompts: [link to prompts/part1-search.md in your repo]
- Current handoff: [link to handoffs/current.md in your repo]

Remaining limitations: city search requires the full city name (no
partial matching yet); no persistence layer yet (CSVs are read-only
in Part 1). Next task: seed SQLite for Part 2 and add booking
create/read/update(cancel)/delete through the frontend.
