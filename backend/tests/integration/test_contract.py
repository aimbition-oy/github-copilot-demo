"""
Cross-service contract test.

Proves that a JWT minted by auth.app.security.create_access_token is accepted
by the backend's get_current_user when both services share the same JWT_SECRET.
"""

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

AUTH_SECURITY_PATH = Path(__file__).parents[3] / "auth" / "app" / "security.py"


def load_auth_security():
    """Dynamically load auth/app/security.py to avoid package name conflicts."""
    spec = importlib.util.spec_from_file_location("auth_security", AUTH_SECURITY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.integration
def test_token_minted_by_auth_accepted_by_backend(client: TestClient):
    """Token created by auth service is valid for backend score submission."""
    auth_security = load_auth_security()
    token = auth_security.create_access_token(
        user_id=42,
        username="contract-user",
        secret="test-secret",
        expire_hours=1,
    )

    resp = client.post(
        "/scores",
        json={"game_slug": "super-mario-bros", "score": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == 42
    assert data["username_cached"] == "contract-user"
    assert data["score"] == 9999


@pytest.mark.integration
def test_token_with_wrong_secret_rejected(client: TestClient):
    """Backend rejects a token signed with a different secret."""
    auth_security = load_auth_security()
    token = auth_security.create_access_token(
        user_id=1,
        username="hacker",
        secret="wrong-secret",
        expire_hours=1,
    )

    resp = client.post(
        "/scores",
        json={"game_slug": "super-mario-bros", "score": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
