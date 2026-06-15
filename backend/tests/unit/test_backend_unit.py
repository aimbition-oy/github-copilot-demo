"""Unit tests for backend security, seed, and schema logic."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db import Base
from app.schemas import ScoreSubmitRequest
from app.security import get_current_user


def _make_credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _settings(secret: str = "test-secret") -> Settings:
    return Settings(jwt_secret=secret, database_url="sqlite:///:memory:")


def _mint_token(
    user_id: int = 1,
    username: str = "testuser",
    secret: str = "test-secret",
    exp_delta: timedelta = timedelta(hours=1),
) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + exp_delta,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


class TestGetCurrentUser:
    def test_valid_token_returns_user(self):
        token = _mint_token(user_id=7, username="hero")
        result = get_current_user(_make_credentials(token), _settings())
        assert result["user_id"] == 7
        assert result["username"] == "hero"

    def test_expired_token_raises_401(self):
        token = _mint_token(exp_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(_make_credentials(token), _settings())
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_wrong_secret_raises_401(self):
        token = _mint_token(secret="wrong-secret")
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(_make_credentials(token), _settings("test-secret"))
        assert exc_info.value.status_code == 401

    def test_malformed_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(_make_credentials("not.a.token"), _settings())
        assert exc_info.value.status_code == 401


class TestSeedGames:
    def _make_session(self):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)()

    def test_seed_games_idempotent(self):
        from app.seed import seed_games
        from app.models import Game

        db = self._make_session()
        seed_games(db)
        seed_games(db)
        count = db.query(Game).count()
        assert count == 10


class TestScoreSubmitRequest:
    def test_negative_score_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ScoreSubmitRequest(game_slug="test-game", score=-1)

    def test_zero_score_is_valid(self):
        req = ScoreSubmitRequest(game_slug="test-game", score=0)
        assert req.score == 0

    def test_positive_score_is_valid(self):
        req = ScoreSubmitRequest(game_slug="test-game", score=99999)
        assert req.score == 99999
