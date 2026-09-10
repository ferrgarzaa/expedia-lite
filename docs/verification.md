# Verification

## Backend

```bash
cd backend
./.venv/bin/pytest -v
```

Expected: 5 passed (city search matches the sample-data README's
"Concrete records to check" table).

## Frontend

```bash
cd frontend
npm run lint
npm run build
```

Expected: 0 lint errors; `dist/` produced with no build errors.

## Manual browser check (Part 1)

| Action | Expected | Observed |
| --- | --- | --- |
| Search "Boston" | 4 rows: T001, T002, T009, T010 | |
| Search "boston" (lowercase) | Same 4 rows | |
| Search "Miami" | "No hotel stays found for..." message | |
| Submit with empty city | Inline validation message, no request sent | |

Fill in the Observed column and attach a screenshot when writing
`report.md`.
