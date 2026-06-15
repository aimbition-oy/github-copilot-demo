"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class GameResponse(BaseModel):
    id: int
    slug: str
    title: str
    year: int
    publisher: str
    cover_art_path: str

    model_config = ConfigDict(from_attributes=True)


class ScoreSubmitRequest(BaseModel):
    game_slug: str
    score: int

    @field_validator("score")
    @classmethod
    def score_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("score must be >= 0")
        return v


class ScoreResponse(BaseModel):
    id: int
    user_id: int
    username_cached: str
    game_id: int
    score: int
    achieved_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    score: int
    achieved_at: datetime
