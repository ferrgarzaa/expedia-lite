# Selected prompts — Part 2 (SQLite CRUD)

The prompts that shaped Part 2, in the order they were used. Each one
was followed by a manual review of the diff in VS Code before the work
was kept.

## 1. Storage and seeding

> Move persistence from the CSVs to SQLite in `backend/`. Create a
> `database.py` that owns the connection, the schema for `hotels`,
> `trips`, `users`, and `bookings`, and a `seed_if_empty()` that loads
> the four supplied CSVs **once**. Seeding must check whether the tables
> already hold rows and return without touching anything if they do, so
> restarting the app never duplicates or reloads the starter records.
> Preserve the supplied ids exactly as they appear in the CSVs.

## 2. Model–View–Controller

> Restructure the backend into the Model–View–Controller split we
> discussed in class. Put the records and their relationships in
> `app/models.py` (`Hotel`, `Trip`, `User`, `Booking`, plus joined views
> for a stay and a booking). Put every SQL statement in
> `app/controllers/`, with a database controller that performs booking
> CRUD. `main.py` must stay a thin FastAPI layer: validate, call one
> controller function, return JSON — no SQL and no join logic.

## 3. Search by hotel name

> The requirement changed: the search input takes a **hotel name**, not
> a city. Update the controller, the FastAPI path
> (`GET /api/search?hotel=...`), and the Vue form and labels. Matching
> should be case-insensitive and should also accept part of a name.
> Keep the distinct "no results" message.

## 4. CRUD through the interface

> Add booking to the search results and a Booking history tab. All four
> CRUD actions must happen through the frontend: create a booking, read
> it back in history, update its status to cancel it **while keeping the
> record**, and delete a test booking. New bookings must get unique ids
> that continue the `B###` sequence without reusing a seeded one.

## 5. Interface quality

> Improve the appearance and usability of the interface using the UI
> research approach from In-class Activity 2. Use one set of design
> tokens across both tabs, one clear primary action per view, explicit
> loading / empty / no-results states, a visible confirmation or error
> message after every action, a confirmation step before deleting, and
> status shown as a labelled badge rather than colour alone. Keep focus
> rings visible and table headers scoped. Do not use blue buttons.

## 6. Verification

> Run the backend tests, the frontend lint, and the production build.
> Then, through the browser, demonstrate each CRUD action on a record
> added after seeding, and verify the changes survive a browser refresh
> and a restart of both servers with no duplicated starter records.
> Record expected and observed results in `docs/verification.md`.
