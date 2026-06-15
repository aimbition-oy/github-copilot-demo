"""Integration tests for auth HTTP routes."""

import pytest
from fastapi.testclient import TestClient

from app.security import create_access_token

pytestmark = pytest.mark.integration


def _register(client: TestClient, username: str = "player1", password: str = "secret123"):
    return client.post("/register", json={"username": username, "password": password})


class TestRegister:
    def test_happy_path(self, client: TestClient):
        resp = _register(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "player1"
        assert "id" in data
        assert "created_at" in data

    def test_duplicate_username(self, client: TestClient):
        _register(client)
        resp = _register(client)
        assert resp.status_code == 409

    def test_short_password_rejected(self, client: TestClient):
        resp = client.post("/register", json={"username": "player1", "password": "hi"})
        assert resp.status_code == 422


class TestLogin:
    def test_correct_credentials(self, client: TestClient):
        _register(client)
        resp = client.post("/login", json={"username": "player1", "password": "secret123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_wrong_password(self, client: TestClient):
        _register(client)
        resp = client.post("/login", json={"username": "player1", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_unknown_user(self, client: TestClient):
        resp = client.post("/login", json={"username": "nobody", "password": "secret123"})
        assert resp.status_code == 401


class TestMe:
    def test_valid_token_returns_user(self, client: TestClient):
        _register(client)
        login_resp = client.post("/login", json={"username": "player1", "password": "secret123"})
        token = login_resp.json()["access_token"]

        resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "player1"

    def test_missing_authorization_header(self, client: TestClient):
        resp = client.get("/me")
        assert resp.status_code == 401

    def test_invalid_token(self, client: TestClient):
        resp = client.get("/me", headers={"Authorization": "Bearer totallyinvalidtoken"})
        assert resp.status_code == 401


class TestHealth:
    def test_health_check(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
