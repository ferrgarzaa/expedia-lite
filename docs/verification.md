# Verification

## Backend

```bash
cd backend
./.venv/bin/pytest -v
```

Expected: 16 passed — 5 in `test_data.py` (CSV join logic, unchanged
from Part 1) and 11 in `test_db.py` (SQLite seeding, search, and
booking CRUD, including a simulated restart).

## Frontend

```bash
cd frontend
npm run lint
npm run build
```

Expected: 0 lint errors; `dist/` produced with no build errors.

## Manual browser check — Part 1 (unchanged)

| Action | Expected | Observed |
| --- | --- | --- |
| Search "Boston" | 4 rows: T001, T002, T009, T010 | |
| Search "Miami" | "No hotel stays found for..." message | |

## Manual browser check — Part 2 (new)

| Action | Expected | Observed |
| --- | --- | --- |
| Open Booking History tab | Table shows the 6 seeded bookings | |
| Click "Book" on a search result, pick a traveler, confirm | Confirmation message with a new booking ID; new row appears in Booking History | |
| Click "Cancel" on a booking in history | Status changes to "cancelled"; row stays in the table | |
| Click "Delete" on the test booking created above | Row disappears from the table | |
| Refresh the browser | All changes (new booking, cancelled status, deletion) still reflected | |
| Stop and restart both `uvicorn` and `npm run dev` | Same data as before restart: seeded rows still present exactly once, no duplicates, prior changes preserved | |

Fill in the Observed column and attach screenshots when writing
`report.md`.
