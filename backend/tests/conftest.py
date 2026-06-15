"""Shared test fixtures for the backend service."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db import Base, get_db, seed_games
from app.main import app

# Make the auth service importable for contract tests
AUTH_PATH = Path(__file__).parent.parent.parent / "auth"
if str(AUTH_PATH) not in sys.path:
    sys.path.insert(0, str(AUTH_PATH))


@pytest.fixture(scope="function")
def test_db():
    """In-memory SQLite database pre-seeded with games."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    seed_games(db)
    db.close()
    yield TestingSession
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(test_db):
    """TestClient with DB and settings dependency overrides applied."""

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
            enable_test_endpoints=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_token(
    user_id: int = 1,
    username: str = "testuser",
    secret: str = "test-secret",
) -> str:
    """Mint a JWT using the same secret as the test settings."""
    import jwt
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, secret, algorithm="HS256")
