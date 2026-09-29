"""Controller for live hotel discovery by U.S. ZIP code (Assignment 2).

Flow:
  1. validate the ZIP (exactly five digits, leading zeros kept);
  2. geocode it with Geoapify and accept ONLY a U.S. ``postcode`` result
     whose postcode equals the requested ZIP — anything else is reported
     as unresolved instead of silently searching a different place;
  3. ask Geoapify Places for hotels within 5 km of that returned point;
  4. turn the GeoJSON features into ``ExternalHotel`` models, keeping
     missing fields as ``None`` (never invented).
"""

import math
import re
from typing import List, Optional, Tuple

from app.models import ExternalHotel, SearchCenter
from app.services import geoapify_client

ZIP_PATTERN = re.compile(r"^\d{5}$")
SEARCH_RADIUS_M = 5000
RESULT_LIMIT = 50


class InvalidZipError(Exception):
    code = "invalid_zip"


class ZipNotResolvedError(Exception):
    code = "zip_not_found"


def validate_zip(raw: str) -> str:
    zip_code = (raw or "").strip()
    if not ZIP_PATTERN.match(zip_code):
        raise InvalidZipError(
            "Enter a five-digit U.S. ZIP code, for example 02134 or 16802."
        )
    return zip_code


def pick_postcode_match(zip_code: str, geocode_json: dict) -> SearchCenter:
    """Return the first U.S. postcode result that is exactly ``zip_code``."""
    for result in geocode_json.get("results") or []:
        if (
            result.get("result_type") == "postcode"
            and (result.get("country_code") or "").lower() == "us"
            and str(result.get("postcode") or "").strip() == zip_code
            and result.get("lat") is not None
            and result.get("lon") is not None
        ):
            return SearchCenter(
                zip_code=zip_code,
                lat=float(result["lat"]),
                lon=float(result["lon"]),
                label=result.get("formatted"),
            )
    raise ZipNotResolvedError(
        f"ZIP code {zip_code} could not be matched to a U.S. postcode "
        "location, so no hotel search was run."
    )


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Great-circle distance in whole meters (haversine)."""
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)))


def _clean(value) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_hotels(center: SearchCenter, places_json: dict) -> List[ExternalHotel]:
    """Convert Places GeoJSON features into models, nearest first."""
    hotels: List[ExternalHotel] = []
    seen = set()
    for feature in places_json.get("features") or []:
        props = feature.get("properties") or {}
        place_id = _clean(props.get("place_id"))
        lat, lon = props.get("lat"), props.get("lon")
        if lat is None or lon is None:
            coords = (feature.get("geometry") or {}).get("coordinates") or []
            if len(coords) == 2:
                lon, lat = coords
        if not place_id or lat is None or lon is None or place_id in seen:
            continue  # cannot be placed on the map or identified
        lat, lon = float(lat), float(lon)
        distance = _distance_m(center.lat, center.lon, lat, lon)
        if distance > SEARCH_RADIUS_M:
            continue  # defensive: keep the stated 5 km promise
        seen.add(place_id)
        name = _clean(props.get("name"))
        address = _clean(props.get("formatted"))
        if name and address and address.startswith(name + ", "):
            address = address[len(name) + 2 :]
        hotels.append(
            ExternalHotel(
                place_id=place_id,
                name=name,
                lat=lat,
                lon=lon,
                address=address,
                distance_m=distance,
                website=_clean(props.get("website")),
            )
        )
    hotels.sort(key=lambda h: h.distance_m)
    return hotels


def find_hotels_near_zip(raw_zip: str) -> Tuple[SearchCenter, List[ExternalHotel]]:
    zip_code = validate_zip(raw_zip)
    center = pick_postcode_match(
        zip_code, geoapify_client.geocode_us_postcode(zip_code)
    )
    places = geoapify_client.hotels_within(
        center.lon, center.lat, SEARCH_RADIUS_M, RESULT_LIMIT
    )
    return center, parse_hotels(center, places)
