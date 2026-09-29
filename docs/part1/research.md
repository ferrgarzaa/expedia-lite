# Assignment 2 · Part 1 — Research notes

Research done before building the ZIP → hotels list + map feature.

## Sources consulted

| # | Source | Link |
| --- | --- | --- |
| 1 | Geoapify Geocoding API (forward geocoding, `type=postcode`, `filter=countrycode:us`) | https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/ |
| 2 | Geoapify Places API (categories, `filter=circle:lon,lat,radius`, `bias=proximity`, `limit` ≤ 500) | https://apidocs.geoapify.com/docs/places/ |
| 3 | Geoapify pricing / free-plan limits | https://www.geoapify.com/pricing/ |
| 4 | Leaflet documentation (markers, `divIcon`, `circle`, `fitBounds`, attribution) | https://leafletjs.com/reference.html |
| 5 | Leaflet accessibility guide | https://leafletjs.com/examples/accessibility/ |
| 6 | OpenStreetMap tile usage policy | https://operations.osmfoundation.org/policies/tiles/ |
| 7 | Google Maps "Hotels" search (existing app) | https://www.google.com/maps/search/hotels |
| 8 | Airbnb / Booking.com map view (existing apps) | https://www.airbnb.com · https://www.booking.com |

## Useful features observed

- **Numbered / labelled pins that match the list** (Google Maps, Booking.com):
  easy to connect a pin with a card without relying on colour.
- **Selecting a card highlights its pin and vice-versa** (Airbnb,
  Booking.com): the pin grows/changes colour and the map pans to it.
- **Search radius drawn on the map** makes clear what area was searched.
- Geoapify Geocoding returns `result_type`, `country_code`, `postcode`
  and `rank.confidence`, so the backend can *check* that the answer really
  is the requested U.S. ZIP instead of trusting the first result.
- Geoapify Places supports `circle:` filters and `bias=proximity`, so
  "within 5 km, nearest first" is one request.
- Leaflet markers are focusable and accept `title`/`alt`, which helps
  keyboard and screen-reader users.

## Problematic features observed

- Commercial apps show **prices, ratings and "Book" buttons on pins**.
  Geoapify has none of this, so copying that pattern would mean inventing
  data — rejected.
- Selection sync is often **hover-only**, which does not work with a
  keyboard or on touch screens.
- Geocoders happily return a *nearby* or *partial* match (another
  postcode, a city, another country). Silently searching that place would
  mislead the traveler.
- Many apps show "0 results" when the request actually failed.
- Default Leaflet marker images break with bundlers (Vite) unless paths
  are fixed; `divIcon` avoids this.
- The OSM tile policy asks for visible attribution and light usage (fine
  for a class demo, not for production traffic).

## Design decisions adopted

1. ZIP is validated as exactly five digits **as text** (leading zeros
   kept) in Vue *and* in FastAPI.
2. The backend accepts only a geocoding result with
   `result_type = postcode`, `country_code = us` and `postcode ==` the
   requested ZIP; otherwise it returns `zip_not_found` and **does not run
   the hotel search**.
3. Places request: `categories=accommodation.hotel`,
   `filter=circle:<lon>,<lat>,5000`, `bias=proximity:<lon>,<lat>`,
   `limit=50`. The backend also drops any result > 5 km and any duplicate
   `place_id`. The 50 cap is shown to the user; results are not claimed to
   be exhaustive.
4. Shown fields: name, address, coordinates and straight-line distance —
   all from the response. Missing name/address get an honest italic label.
   No price, rating, availability or booking button.
5. Numbered pins = numbered list items. Click **or Enter/Space** on
   either side sets one shared `selectedId`; the pin turns dark plum and
   grows, the map pans and opens a popup, and the list item gets an
   plum border and scrolls into view (colour is never the only cue).
6. Separate messages for loading, results, invalid input, ZIP not found,
   no nearby hotels, and failure (network, provider error, rate limit,
   missing key). A failure never renders as "0 hotels".
7. All Geoapify calls go through FastAPI; the key lives only in
   `backend/.env` (git-ignored). The browser only loads OSM tiles, which
   need no key.
8. Attribution (Leaflet, OpenStreetMap, Geoapify) stays visible.
