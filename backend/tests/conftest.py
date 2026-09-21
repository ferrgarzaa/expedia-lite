"""Shared fixtures: a freshly seeded SQLite database per test."""

import pytest

from app.database import init_db, seed_if_empty


@pytest.fixture()
def seeded_db(tmp_path):
    """Create and seed a throwaway database, returning its path."""
    db_path = tmp_path / "expedia_lite.db"
    init_db(db_path)
    seed_if_empty(db_path)
    return db_path
