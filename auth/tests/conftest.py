"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for the duration of a single test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    yield TestingSession
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Return a TestClient with DB and settings overrides applied."""

    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    def override_get_settings():
        return Settings(
            jwt_secret="test-secret",
            database_url="sqlite:///:memory:",
            cors_origins="http://localhost:5173",
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
