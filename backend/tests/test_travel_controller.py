"""Tests for the read controller: hotel-name search and travelers.

Expected trip IDs come from the instructor's sample data README
("Concrete records to check" table).
"""

from app.controllers import travel_controller


def test_search_by_full_hotel_name(seeded_db):
    ids = {
        o.trip.trip_id
        for o in travel_controller.search_stays_by_hotel_name(
            "Harbor Lantern Hotel", seeded_db
        )
    }
    assert ids == {"T001", "T009"}


def test_search_is_case_insensitive(seeded_db):
    lower = travel_controller.search_stays_by_hotel_name(
        "harbor lantern hotel", seeded_db
    )
    upper = travel_controller.search_stays_by_hotel_name(
        "HARBOR LANTERN HOTEL", seeded_db
    )
    assert {o.trip.trip_id for o in lower} == {o.trip.trip_id for o in upper}


def test_search_matches_a_partial_hotel_name(seeded_db):
    ids = {
        o.trip.trip_id
        for o in travel_controller.search_stays_by_hotel_name(
            "harbor", seeded_db
        )
    }
    assert ids == {"T001", "T009"}


def test_hotel_name_with_no_stays_returns_empty_list(seeded_db):
    assert (
        travel_controller.search_stays_by_hotel_name("Hotel Miami", seeded_db)
        == []
    )


def test_result_joins_the_hotel_and_derives_nights_and_price(seeded_db):
    offer = travel_controller.search_stays_by_hotel_name(
        "Harbor Lantern Hotel", seeded_db
    )[0]
    row = offer.to_dict()
    assert row["hotel_name"] == "Harbor Lantern Hotel"
    assert row["city"] == "Boston"
    assert row["nights"] == 2
    assert row["stay_price_usd"] == round(2 * row["nightly_rate_usd"], 2)


def test_blank_query_returns_nothing(seeded_db):
    assert travel_controller.search_stays_by_hotel_name("   ", seeded_db) == []


def test_demo_travelers_are_available(seeded_db):
    users = travel_controller.list_users(seeded_db)
    assert len(users) >= 1
    assert users[0].user_id == "U001"
