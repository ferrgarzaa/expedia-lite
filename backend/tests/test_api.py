"""End-to-end tests for the FastAPI layer against a throwaway database."""

import pytest
from fastapi.testclient import TestClient

from app import database, main


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "expedia_lite.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(
        "app.controllers.travel_controller.DB_PATH", db_path, raising=False
    )
    monkeypatch.setattr(
        "app.controllers.booking_controller.DB_PATH", db_path, raising=False
    )
    with TestClient(main.app) as test_client:
        yield test_client


def test_search_endpoint_returns_matching_stays(client):
    body = client.get("/api/search", params={"hotel": "Harbor"}).json()
    assert body["count"] == 2
    assert {r["trip_id"] for r in body["results"]} == {"T001", "T009"}


def test_search_endpoint_reports_no_matches(client):
    body = client.get("/api/search", params={"hotel": "Hotel Miami"}).json()
    assert body["count"] == 0
    assert body["results"] == []


def test_full_crud_cycle_through_the_api(client):
    history = client.get("/api/bookings").json()
    seeded_count = history["count"]

    created = client.post(
        "/api/bookings", json={"user_id": "U002", "trip_id": "T004"}
    )
    assert created.status_code == 201
    booking_id = created.json()["booking_id"]

    after_create = client.get("/api/bookings").json()
    assert after_create["count"] == seeded_count + 1

    cancelled = client.patch(
        f"/api/bookings/{booking_id}", json={"status": "cancelled"}
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    after_cancel = client.get("/api/bookings").json()
    assert after_cancel["count"] == seeded_count + 1  # record retained

    deleted = client.delete(f"/api/bookings/{booking_id}")
    assert deleted.status_code == 200

    after_delete = client.get("/api/bookings").json()
    assert after_delete["count"] == seeded_count
    assert booking_id not in {r["booking_id"] for r in after_delete["results"]}


def test_users_endpoint_lists_demo_travelers(client):
    body = client.get("/api/users").json()
    assert body["count"] >= 1
    assert body["results"][0]["user_id"] == "U001"


def test_deleting_an_unknown_booking_is_a_404(client):
    assert client.delete("/api/bookings/B999").status_code == 404
