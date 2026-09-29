# Assignment 2 · Part 1 — Verification record

## A. Automated checks (labeled fixed JSON samples — not live data)

Fixtures: [`backend/tests/fixtures/`](../../backend/tests/fixtures/) ·
tests: [`backend/tests/test_hotel_discovery.py`](../../backend/tests/test_hotel_discovery.py).
Repeat with `cd backend && .venv/bin/pytest -q`.

| Input / action | Expected | Observed (2026-09-29) |
| --- | --- | --- |
| ZIP `""`, `1680`, `168021`, `16a02`, `16802-1234`, spaces | 422 `invalid_zip`, provider **not** called | Pass (6 cases) |
| ZIP `02134` | Kept as `"02134"` (leading zero) | Pass |
| ZIP 16802 + sample places | Center = sample lat/lon; ids nearest first; >5 km and duplicate `place_id` removed; unnamed place keeps `name: null`; no price/rating keys | Pass |
| Geocoder returns 16801 + a city for 16802 | 404 `zip_not_found`; Places **not** called | Pass |
| Geocoder returns nothing | 404 `zip_not_found` | Pass |
| Places returns no features | 200, `count: 0` | Pass |
| Provider HTTP 429 | 503 `rate_limited`, no `results` key | Pass |
| Provider HTTP 401 | 502 `provider_auth` | Pass |
| Provider HTTP 500 / timeout | 502 `provider_unavailable` | Pass |
| No `GEOAPIFY_API_KEY` | 503 `missing_api_key` | Pass |
| Whole suite (incl. Assignment 1 tests) | all pass | 39 passed |
| `npm run lint` / `npm run build` | 0 errors / build succeeds | 0 errors / built |

## B. Interface checks in sample mode (Playwright, fixtures, not live data)

Started with `backend/.venv/bin/python backend/scripts/run_with_samples.py`
and `npm run dev`.

| Action | Expected | Observed |
| --- | --- | --- |
| Type `1680`, Enter | "Invalid ZIP code…" | Shown ([screenshot](sample-mode-invalid.png)) |
| `00000` | "ZIP code not found… no hotel search was run" | Shown ([screenshot](sample-mode-notfound.png)) |
| `99999` (sample with no hotels) | "No hotels found within 5 km…" | Shown ([screenshot](sample-mode-empty.png)) |
| `50000` (simulated failure) | Red "Search failed — this is not an empty result" | Shown ([screenshot](sample-mode-error.png)) |
| `42900` (simulated 429) | Red failure message mentioning the limit | Shown ([screenshot](sample-mode-ratelimit.png)) |
| `16802` | List + numbered pins + 5 km circle | 3 sample hotels ([screenshot](sample-mode-results.png)) |
| Click list item 2 | Pin 2 turns orange, popup "2. Sample Campus Inn" | Pass |
| Tab to pin 3, press Enter | List item 3 highlighted (`aria-pressed=true`), label "Selected: 3. Name not provided by source" | Pass ([screenshot](sample-mode-selected.png)) |
| Attribution | Visible | "Leaflet \| © OpenStreetMap contributors \| Hotel data © Geoapify" |

## C. Live searches (fill in after running with your own key)

| ZIP | Observation date | Expected | Observed |
| --- | --- | --- | --- |
| 16802 | 2026-09-__ | Center near State College, PA; hotels ≤ 5 km, names/coords match the response | _fill in_ |
| 02134 (leading zero) | 2026-09-__ | Center in Allston/Boston, MA (not 2134) | _fill in_ |
| 00000 | 2026-09-__ | "ZIP code not found", no hotels | _fill in_ |
| 1234 | 2026-09-__ | "Invalid ZIP code" (no request sent) | _fill in_ |

Check that names match the provider: open DevTools → Network →
`/api/hotels/nearby?zip=…` and compare with the list.

## Limitations

- Geoapify coverage comes from OpenStreetMap-based data; some hotels are
  missing or unnamed. Results are not an exhaustive or bookable inventory.
- At most 50 hotels are requested; the UI says so.
- Distance is straight-line from the Geoapify postcode point, not
  driving distance, and not from the traveler's location.
- OSM tiles are for light demo use only (tile usage policy).
