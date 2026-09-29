# Expedia Lite — Assignment 2 · Part 1: Live Hotel Search and Map

## 1. Project access

- **Repository:** https://github.com/ferrgarzaa/expedia-lite
- **Assessed commit:** `3f7d8ae521c3e79f1e9e15ce80350ce795063894` (branch `main`; contains all Part 1 code — the only later commit fills in this report's live results and video link)
- **Stack:** Vue 3 + Vite (View), FastAPI (HTTP), Python controllers and
  models, SQLite (Assignment 1 data), Geoapify Geocoding + Places, Leaflet
  with OpenStreetMap tiles.

### Startup and configuration

```bash
# Backend
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env            # put GEOAPIFY_API_KEY=<your key> in backend/.env
./.venv/bin/pytest -q           # 39 tests, no live API calls
./.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install                     # includes leaflet@1.9.4
npm run dev                     # http://localhost:5173 → tab "Hotels near a ZIP"
```

- The Geoapify key is read only by FastAPI from `backend/.env`.
  `.env` is in `.gitignore` and is not tracked; only `backend/.env.example`
  (placeholder value) is committed. The frontend never receives the key.
- Map tiles come from OpenStreetMap, which needs no browser credential.
  Attribution (Leaflet, OpenStreetMap, Geoapify) is always visible.
- Optional offline mode with labeled sample data (no key, no quota):
  `./.venv/bin/python scripts/run_with_samples.py`.

### What was built

| Layer | File | Responsibility |
| --- | --- | --- |
| Gateway | `backend/app/services/geoapify_client.py` | Only code that calls Geoapify; maps timeouts, 401/403, 429, 5xx to typed errors |
| Controller | `backend/app/controllers/hotel_discovery_controller.py` | Validates the ZIP, accepts only an exact U.S. postcode match, requests hotels within 5 km, parses results honestly |
| Model | `backend/app/models.py` → `SearchCenter`, `ExternalHotel` | Provider `place_id`, name, coordinates, address, distance — **no** price/rating/availability |
| HTTP | `backend/app/main.py` → `GET /api/hotels/nearby?zip=` | Returns results or a coded error (422 / 404 / 502 / 503) |
| View | `frontend/src/components/HotelDiscovery.vue`, `HotelMap.vue`, `api.js` | ZIP form, status messages, numbered list, Leaflet map, shared selection |

Geoapify requests: Geocoding `type=postcode&filter=countrycode:us`;
Places `categories=accommodation.hotel&filter=circle:<lon>,<lat>,5000&bias=proximity:<lon>,<lat>&limit=50`.

## 2. Research notes

Full notes: [docs/part1/research.md](https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/part1/research.md)

**Sources:** [Geoapify Geocoding](https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/),
[Geoapify Places](https://apidocs.geoapify.com/docs/places/),
[Geoapify pricing](https://www.geoapify.com/pricing/),
[Leaflet reference](https://leafletjs.com/reference.html),
[Leaflet accessibility](https://leafletjs.com/examples/accessibility/),
[OSM tile policy](https://operations.osmfoundation.org/policies/tiles/),
and the map views of [Google Maps hotels](https://www.google.com/maps/search/hotels),
[Airbnb](https://www.airbnb.com) and [Booking.com](https://www.booking.com).

**Useful:** numbered pins that match list cards; selecting a card
highlights the pin and vice-versa; the searched area drawn on the map;
Geoapify returns `result_type`, `country_code` and `postcode`, so the ZIP
match can be verified; Places supports a 5 km circle plus nearest-first
ordering in one call.

**Problematic:** commercial apps put prices, ratings and "Book" on pins
(Geoapify has none — copying it would invent data); sync is often
hover-only (no keyboard/touch); geocoders return nearby or partial matches
that could silently become another place; apps often show "0 results"
when a request failed; Leaflet default marker images break under Vite.

**Decisions:** strict 5-digit text ZIP (leading zeros kept) checked in
Vue and FastAPI; accept only `postcode` + `us` + exact ZIP, otherwise
"ZIP not found" and no hotel request; show only name, address,
coordinates and straight-line distance with honest labels for missing
fields; numbered `divIcon` pins matching list numbers; click **or
Enter/Space** on either side selects the same hotel (darker plum + larger pin,
map pans and opens a popup, list item gets a border and scrolls into
view); one status area with separate messages for each state; the 50-result
cap and "not an exhaustive inventory" are stated in the UI.

## 3. Early mockup

![Part 1 early mockup](https://raw.githubusercontent.com/ferrgarzaa/expedia-lite/main/docs/part1/mockup-part1.png)

Annotated wireframe: ZIP form, one status line, numbered list on the left,
Leaflet map with a 5 km circle and ZIP center on the right, and the text
for the other states.

**Changes during implementation:**
- Added a "Search center: … (lat, lon)" line above the list so users see
  exactly which point was searched.
- The status message for results also shows the source, the 50-result
  cap and the retrieval time.
- Distances under 1 km are shown in meters (the "≈ 0.0 km" in early tests
  was misleading).
- A "Selected: …" line under the map repeats the selection in text and
  links to the hotel website only when the provider supplied one.
- The whole interface was re-themed pink (accent `#be185d`, text
  contrast ≥ 4.5:1) at the student's request; the selected hotel uses a
  darker plum instead of the mockup's orange so it stays distinct from the
  pink accent (and is also marked by size, border and `aria-pressed`).
- Rate-limit and missing-key errors were added as their own failure
  messages (the mockup had a single "failed" state).

## 4. Demo video

https://drive.google.com/file/d/1DhWoHYMG8MAaKdKsv5mnRoEnr12ZlHLf/view?usp=sharing

The video shows: startup, a live search for a valid ZIP, clicking a list
item (pin highlights) and a pin (list highlights), keyboard selection
with Tab + Enter, a ZIP with a leading zero (02134), an invalid ZIP
(1234), an unresolved ZIP (00000), and — using sample mode — no results
and a simulated failure/rate limit.

## 5. Verification record

Full record: [docs/part1/verification.md](https://github.com/ferrgarzaa/expedia-lite/blob/main/docs/part1/verification.md)

### Automated (labeled fixed JSON samples, not live data) — 2026-09-29

| Input / action | Expected | Observed |
| --- | --- | --- |
| ZIPs `1680`, `168021`, `16a02`, `16802-1234`, blank | 422 `invalid_zip`; provider not called | Pass |
| `02134` | Kept as text with leading zero | Pass |
| 16802 + sample Places response | Nearest first; >5 km and duplicate `place_id` dropped; unnamed place stays `null`; no price/rating fields | Pass |
| Geocoder answers 16801 / a city for 16802 | 404 `zip_not_found`; Places not called | Pass |
| Places returns no features | 200 with `count: 0` ("No hotels found") | Pass |
| Provider 429 | 503 `rate_limited`, no results list | Pass |
| Provider 401 / 500 / timeout | 502 coded error, no results list | Pass |
| No API key | 503 `missing_api_key` | Pass |
| `pytest` (all, incl. Assignment 1) · `npm run lint` · `npm run build` | Pass | 39 passed · 0 errors · built |
| UI (Playwright, sample mode): each state; click list → pin; Tab to pin + Enter → list | Correct message per state; selection synced both ways | Pass (screenshots in `docs/part1/`) |

### Live searches

| ZIP | Observation date | Expected | Observed |
| --- | --- | --- | --- |
| 16802 | 2026-09-29 | Center in State College, PA; hotels ≤ 5 km; list names/coords equal the `/api/hotels/nearby` response | Center "State College, PA 16802" (40.8032, -77.8614); 21 hotels, nearest first — 1. Scholar Hotel State College (≈ 970 m), 2. Hotel State College (≈ 1000 m), 3. Nittany Lion Inn (≈ 1.0 km); numbered pins inside the 5 km circle. Clicking a list item highlighted its pin and clicking a pin highlighted the list item; Tab + Enter on a pin also worked |
| 02134 | 2026-09-29 | Leading zero kept; U.S. postcode center; hotels ≤ 5 km | Search ran for 02134 (leading zero kept); 50 hotels returned — the 50-result cap was reached, so more hotels may exist in the area |
| 00000 | 2026-09-29 | "ZIP code not found", no hotel search | "ZIP code not found. ZIP code 00000 could not be matched to a U.S. postcode location, so no hotel search was run." |
| 1234 | 2026-09-29 | "Invalid ZIP code", no request | "Invalid ZIP code. Enter exactly five digits, for example 16802 or 02134 (keep leading zeros)." |

### Corrections and remaining limitations

- Corrected: marker keyboard selection (see AI log), a wrong test
  expectation, and "0.0 km" distance text.
- Geoapify's hotel data is OpenStreetMap-based: some hotels are missing
  or unnamed, and results are capped at 50. The app does not claim an
  exhaustive or bookable inventory and shows no prices.
- Distance is straight-line from the Geoapify postcode point — not
  driving distance and not from the traveler's location.
- OpenStreetMap tiles are suitable only for light demo use.
- Live results change over time, so no check depends on a live count.
- For dense areas such as 02134 the 50-result cap is reached; the UI states "up to 50 shown".

## 6. AI disclosure and evidence log

| Tool | Model | Use |
| --- | --- | --- |
| Claude (Cowork mode, Claude desktop app) | `claude-opus-5-5` | Located the repo, read the API docs, implemented backend and frontend changes, wrote tests and fixtures, ran Playwright UI checks, drafted the mockup, research notes and this report |

Prompt excerpts and decisions: [prompts/a2-part1-live-search.md](https://github.com/ferrgarzaa/expedia-lite/blob/main/prompts/a2-part1-live-search.md)

- *Prompt:* "ocupo que me ayudes hacer esto porfavor" + the assignment
  brief → plan and implementation of the gateway / controller / model /
  endpoint / Vue components.
- *Dependency (CHECK → ACTION → VERIFY):* agent proposed exactly
  `npm install leaflet@1.9.4`; student replied "Sí, apruebo"; verified by
  lint + build.
- *Decision:* rejected "use the first geocoding result" in favor of an
  exact U.S. postcode match (`pick_postcode_match`, tested).
- *Failed / revised approach:* pressing Enter on a Leaflet marker did not
  select it; two fixes failed (element not yet created; TDZ error) before
  the final fix (set the map view first, bind in the marker `add` event).
  Re-verified with Playwright.
- *Failed test:* a sample-ordering expectation was wrong; distances were
  recomputed and the test corrected.

All AI-generated code was reviewed by the student before committing. No
credentials appear in this report, the repository, or the recordings.
