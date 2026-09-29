"""Gateway to the Geoapify HTTP APIs (backend only).

This module is the only code that talks to Geoapify. It sends requests,
maps transport and HTTP problems to typed errors, and returns the raw
JSON. It does not interpret results — that is the controller's job.

The API key never leaves the backend: the Vue View calls FastAPI, and
FastAPI calls Geoapify.
"""

import httpx

from app.config import geoapify_api_key

GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"
TIMEOUT_SECONDS = 10.0


class ProviderError(Exception):
    """Geoapify could not be used. ``code`` is shown to the View."""

    code = "provider_error"
    status_code = 502


class MissingApiKeyError(ProviderError):
    code = "missing_api_key"
    status_code = 503


class ProviderRateLimitedError(ProviderError):
    code = "rate_limited"
    status_code = 503


class ProviderAuthError(ProviderError):
    code = "provider_auth"
    status_code = 502


class ProviderUnavailableError(ProviderError):
    code = "provider_unavailable"
    status_code = 502


def _get(url: str, params: dict) -> dict:
    key = geoapify_api_key()
    if key is None:
        raise MissingApiKeyError(
            "The hotel search service is not configured (missing "
            "GEOAPIFY_API_KEY in backend/.env)."
        )
    try:
        response = httpx.get(
            url, params={**params, "apiKey": key}, timeout=TIMEOUT_SECONDS
        )
    except httpx.HTTPError as error:
        raise ProviderUnavailableError(
            "The hotel search provider could not be reached."
        ) from error

    if response.status_code == 429:
        raise ProviderRateLimitedError(
            "The hotel search provider's request limit was reached. "
            "Please wait a moment and try again."
        )
    if response.status_code in (401, 403):
        raise ProviderAuthError(
            "The hotel search provider rejected the server's credentials."
        )
    if response.status_code >= 400:
        raise ProviderUnavailableError(
            f"The hotel search provider returned an error "
            f"({response.status_code})."
        )
    try:
        return response.json()
    except ValueError as error:
        raise ProviderUnavailableError(
            "The hotel search provider sent an unreadable response."
        ) from error


def geocode_us_postcode(zip_code: str) -> dict:
    """Ask Geoapify for U.S. postcode locations matching ``zip_code``."""
    return _get(
        GEOCODE_URL,
        {
            "postcode": zip_code,
            "type": "postcode",
            "filter": "countrycode:us",
            "format": "json",
            "limit": 5,
        },
    )


def hotels_within(lon: float, lat: float, radius_m: int, limit: int) -> dict:
    """Ask Geoapify Places for hotels inside a circle, nearest first."""
    return _get(
        PLACES_URL,
        {
            "categories": "accommodation.hotel",
            "filter": f"circle:{lon},{lat},{radius_m}",
            "bias": f"proximity:{lon},{lat}",
            "limit": limit,
        },
    )
