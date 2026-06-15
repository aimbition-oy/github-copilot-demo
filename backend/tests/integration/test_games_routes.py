"""Integration tests for the /games routes."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


class TestListGames:
    def test_returns_200_and_10_games(self, client: TestClient):
        resp = client.get("/games")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 10


class TestGetGame:
    def test_known_slug_returns_game(self, client: TestClient):
        resp = client.get("/games/super-mario-bros")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Super Mario Bros."
        assert data["slug"] == "super-mario-bros"

    def test_unknown_slug_returns_404(self, client: TestClient):
        resp = client.get("/games/nonexistent-slug")
        assert resp.status_code == 404
