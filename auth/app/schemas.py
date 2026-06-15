"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    """Request body for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response body containing a JWT access token."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public representation of a user."""

    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
