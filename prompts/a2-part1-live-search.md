# Selected prompts — Assignment 2 · Part 1 (live hotel search + map)

Tool: Claude (Cowork mode in the Claude desktop app), model `claude-opus-5-5`.

## 1. Scope and plan

> ocupo que me ayudes hacer esto porfavor — [pasted the Assignment 2
> brief and the Part 1 submission requirements]

Outcome: the agent located the existing `expedia-lite` repository, read
`AGENTS.md` and `README.md`, read the Geoapify Geocoding and Places docs,
and proposed a plan: gateway (`services/geoapify_client.py`) → controller
(`hotel_discovery_controller.py`) → models (`SearchCenter`,
`ExternalHotel`) → FastAPI path → Vue list + Leaflet map.

## 2. Dependency (CHECK → TAKE ACTION → VERIFY)

> Agent: "Leaflet is not installed. I propose exactly
> `npm install leaflet@1.9.4` in `frontend/` (no other dependencies; the
> backend uses httpx, which is already in requirements.txt). Approve?"
> Student: "Sí, apruebo".

Verified with `npm run lint` and `npm run build` (both passed).

## 3. Honest ZIP resolution (decision)

The first idea was to take the first geocoding result. Rejected after
reading the docs: the geocoder can return a nearby postcode, a city or a
different country. Final rule in `pick_postcode_match()`: accept only
`result_type=postcode`, `country_code=us`, `postcode == ZIP`; otherwise
return `zip_not_found` and do not call Places. Covered by
`test_different_postcode_is_not_silently_searched`.

## 4. Failed / revised approaches

- **Test expectation was wrong.** The first version of
  `test_results_match_sample_and_are_honest` expected the unnamed sample
  hotel to be 2nd nearest. pytest failed (`sample-b != sample-unnamed`).
  Recomputing distances (≈0.76 km vs ≈1.2 km) showed the code was right
  and the expectation wrong; the test was corrected.
- **Keyboard selection on map markers failed.** Pressing Enter on a
  focused Leaflet marker did not select the hotel (Playwright check:
  list had no `aria-pressed=true`). First fix — a `keydown` listener
  added right after `addTo()` — still failed because Leaflet creates
  marker elements only after the map has a view, so `getElement()` was
  `null`. Second attempt with `.on('add', () => bindKeyboard(marker…))`
  threw a TDZ error (`marker` used before initialization). Final fix:
  call `fitBounds` before adding markers and bind in the `add` event
  using `event.target`. Re-check passed: Tab to pin 3 + Enter highlights
  list item 3.
- **Distance display** showed "≈ 0.0 km" for very close hotels; changed
  to meters under 1 km.

## 5. Verification prompt

> Run pytest, lint, build, then drive the UI in sample mode for every
> state (invalid, not found, empty, failure, rate limit, results) and
> both selection directions.

Evidence: [docs/part1/verification.md](../docs/part1/verification.md).
