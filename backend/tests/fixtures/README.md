# Labeled fixed JSON samples (NOT live data)

These files are hand-made samples shaped like Geoapify responses. They
let the tests run repeatably without an API key and without spending the
free-plan quota. Names and coordinates are illustrative; they are not an
observation of the live service.

| File | Shape of | Used to check |
| --- | --- | --- |
| `geocode_16802.json` | Geocoding `format=json` | ZIP 16802 resolves to a U.S. postcode |
| `geocode_wrong_postcode.json` | Geocoding `format=json` | a nearby/different postcode is NOT accepted |
| `geocode_empty.json` | Geocoding `format=json` | unresolved ZIP |
| `places_16802.json` | Places GeoJSON | list parsing, missing name, >5 km, duplicate id |
| `places_empty.json` | Places GeoJSON | honest "no nearby hotels" |
