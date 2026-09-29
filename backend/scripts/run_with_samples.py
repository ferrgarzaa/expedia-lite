"""Run the API with Geoapify replaced by the labeled fixed JSON samples.

For offline UI checks only — nothing here is live data. Special ZIPs:
  16802 -> sample hotels     00000 -> unresolved ZIP
  99999 -> no nearby hotels  50000 -> simulated provider failure
  42900 -> simulated rate limit (HTTP 429)

Usage (from backend/):  .venv/bin/python scripts/run_with_samples.py
"""

import json
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import geoapify_client as g  # noqa: E402

FIX = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


def _load(name):
    return json.loads((FIX / name).read_text())


def geocode(zip_code):
    if zip_code == "50000":
        raise g.ProviderUnavailableError("Simulated provider failure (sample mode).")
    if zip_code == "42900":
        raise g.ProviderRateLimitedError("Simulated rate limit (sample mode). Please wait and retry.")
    if zip_code == "00000":
        return _load("geocode_empty.json")
    data = _load("geocode_16802.json")
    data["results"][0]["postcode"] = zip_code
    return data


def places(lon, lat, radius, limit):
    if abs(lat - 40.7982) > 1e-6:
        return _load("places_empty.json")
    return _load("places_16802.json")


def geocode_switch(zip_code):
    data = geocode(zip_code)
    if zip_code == "99999":
        data["results"][0]["lat"] = 41.0
        data["results"][0]["formatted"] = "Sample ZIP 99999 (no hotels in sample)"
    return data


g.geocode_us_postcode = geocode_switch
g.hotels_within = places

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
