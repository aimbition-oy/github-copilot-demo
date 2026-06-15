"""Integration tests for the /scores and /leaderboard routes."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_token

pytestmark = pytest.mark.integration


class TestSubmitScore:
    def test_missing_auth_header_returns_4xx(self, client: TestClient):
        resp = client.post("/scores", json={"game_slug": "super-mario-bros", "score": 100})
        assert resp.status_code in (401, 403)

    def test_invalid_token_returns_401(self, client: TestClient):
        resp = client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": 100},
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401

    def test_valid_token_and_game_returns_201(self, client: TestClient):
        token = make_token(user_id=1, username="player1")
        resp = client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": 5000},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["score"] == 5000
        assert data["user_id"] == 1
        assert data["username_cached"] == "player1"

    def test_valid_token_unknown_slug_returns_404(self, client: TestClient):
        token = make_token()
        resp = client.post(
            "/scores",
            json={"game_slug": "does-not-exist", "score": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    def test_negative_score_returns_422(self, client: TestClient):
        token = make_token()
        resp = client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": -1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


class TestLeaderboard:
    def test_empty_leaderboard_returns_empty_list(self, client: TestClient):
        resp = client.get("/games/super-mario-bros/leaderboard")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_scores_returned_sorted_desc(self, client: TestClient):
        token = make_token(user_id=1, username="alice")
        for score_val in [100, 500, 250]:
            client.post(
                "/scores",
                json={"game_slug": "super-mario-bros", "score": score_val},
                headers={"Authorization": f"Bearer {token}"},
            )

        resp = client.get("/games/super-mario-bros/leaderboard")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["score"] == 500
        assert data[1]["score"] == 250
        assert data[2]["score"] == 100
        assert data[0]["rank"] == 1

    def test_limit_query_param_respected(self, client: TestClient):
        token = make_token(user_id=2, username="bob")
        for score_val in [10, 20, 30, 40, 50]:
            client.post(
                "/scores",
                json={"game_slug": "super-mario-bros", "score": score_val},
                headers={"Authorization": f"Bearer {token}"},
            )

        resp = client.get("/games/super-mario-bros/leaderboard?limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["score"] == 50


class TestDeleteScores:
    def test_delete_all_scores_returns_count(self, client: TestClient):
        token = make_token()
        for i in range(3):
            client.post(
                "/scores",
                json={"game_slug": "tetris", "score": i * 100},
                headers={"Authorization": f"Bearer {token}"},
            )

        resp = client.delete("/test/scores")
        assert resp.status_code == 200
        assert resp.json()["deleted"] == 3

        # Verify leaderboard is now empty
        lb = client.get("/games/tetris/leaderboard")
        assert lb.json() == []
