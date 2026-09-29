"""Tests for live hotel discovery using labeled fixed JSON samples.

No test calls Geoapify: the gateway functions are replaced with fixture
data, so results are repeatable and no quota is used. Assertions never
depend on a live result count.
"""

import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.controllers import hotel_discovery_controller as ctl
from app.services import geoapify_client

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture()
def client():
    return TestClient(main.app)


def fake_provider(monkeypatch, geocode, places):
    calls = {"geocode": 0, "places": 0}

    def _geo(zip_code):
        calls["geocode"] += 1
        return load(geocode)

    def _places(lon, lat, radius, limit):
        calls["places"] += 1
        assert radius == 5000
        return load(places)

    monkeypatch.setattr(geoapify_client, "geocode_us_postcode", _geo)
    monkeypatch.setattr(geoapify_client, "hotels_within", _places)
    return calls


@pytest.mark.parametrize("bad", ["", "1680", "168021", "16a02", "16802-1234", "  "])
def test_invalid_zip_rejected_without_calling_provider(client, monkeypatch, bad):
    calls = fake_provider(monkeypatch, "geocode_16802.json", "places_16802.json")
    r = client.get("/api/hotels/nearby", params={"zip": bad})
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "invalid_zip"
    assert calls == {"geocode": 0, "places": 0}


def test_leading_zero_zip_is_kept():
    assert ctl.validate_zip("02134") == "02134"


def test_results_match_sample_and_are_honest(client, monkeypatch):
    fake_provider(monkeypatch, "geocode_16802.json", "places_16802.json")
    body = client.get("/api/hotels/nearby", params={"zip": "16802"}).json()
    assert body["center"]["lat"] == 40.7982 and body["center"]["lon"] == -77.8599
    ids = [h["place_id"] for h in body["results"]]
    # nearest first, >5 km dropped, duplicate provider id dropped
    assert ids == ["sample-a", "sample-b", "sample-unnamed"]
    unnamed = body["results"][2]
    assert unnamed["name"] is None and unnamed["address"] is None
    for h in body["results"]:
        assert set(h) == {"place_id", "name", "lat", "lon", "address",
                          "distance_m", "website", "source"}
        assert "price" not in json.dumps(h) and "rating" not in json.dumps(h)
    assert body["results"][0]["address"].startswith("100 Example St")


def test_different_postcode_is_not_silently_searched(client, monkeypatch):
    calls = fake_provider(monkeypatch, "geocode_wrong_postcode.json", "places_16802.json")
    r = client.get("/api/hotels/nearby", params={"zip": "16802"})
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "zip_not_found"
    assert calls["places"] == 0


def test_unresolved_zip(client, monkeypatch):
    fake_provider(monkeypatch, "geocode_empty.json", "places_16802.json")
    r = client.get("/api/hotels/nearby", params={"zip": "00000"})
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "zip_not_found"


def test_no_nearby_hotels_is_a_successful_empty_search(client, monkeypatch):
    fake_provider(monkeypatch, "geocode_16802.json", "places_empty.json")
    r = client.get("/api/hotels/nearby", params={"zip": "16802"})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def _fake_http(monkeypatch, status=None, exc=None):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "test-key-not-real")

    def _get(url, params, timeout):
        if exc:
            raise exc
        return httpx.Response(status, json={"message": "x"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(geoapify_client.httpx, "get", _get)


@pytest.mark.parametrize(
    "status,exc,code,http",
    [
        (429, None, "rate_limited", 503),
        (401, None, "provider_auth", 502),
        (500, None, "provider_unavailable", 502),
        (None, httpx.ConnectTimeout("t"), "provider_unavailable", 502),
    ],
)
def test_provider_failures_are_not_empty_results(client, monkeypatch, status, exc, code, http):
    _fake_http(monkeypatch, status, exc)
    r = client.get("/api/hotels/nearby", params={"zip": "16802"})
    assert r.status_code == http
    assert r.json()["detail"]["code"] == code
    assert "results" not in r.json()


def test_missing_key_reported(client, monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    r = client.get("/api/hotels/nearby", params={"zip": "16802"})
    assert r.status_code == 503
    assert r.json()["detail"]["code"] == "missing_api_key"
