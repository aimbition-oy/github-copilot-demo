"""Integration tests for GET /users/{username}/scores."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.models import Game, Score
from tests.conftest import make_token

pytestmark = pytest.mark.integration


def _insert_scores(test_db, username: str, user_id: int, entries: list[dict]) -> None:
    # Direct DB insertion to control achieved_at; POST /scores sets it server-side only.
    db = test_db()
    try:
        for entry in entries:
            game = db.query(Game).filter(Game.slug == entry["game_slug"]).first()
            db.add(
                Score(
                    user_id=user_id,
                    username_cached=username,
                    game_id=game.id,
                    score=entry["score"],
                    achieved_at=entry["achieved_at"],
                )
            )
        db.commit()
    finally:
        db.close()


class TestPlayerScoreHistory:
    def test_newest_first_ordering(self, client: TestClient, test_db):
        # TC1: Scores are returned newest-first (achieved_at DESC).
        t1 = datetime(2024, 1, 1, 10, 0, 0)
        t2 = datetime(2024, 1, 2, 10, 0, 0)
        t3 = datetime(2024, 1, 3, 10, 0, 0)
        _insert_scores(
            test_db,
            "alice",
            1,
            [
                {"game_slug": "super-mario-bros", "score": 100, "achieved_at": t1},
                {"game_slug": "super-mario-bros", "score": 200, "achieved_at": t3},
                {"game_slug": "super-mario-bros", "score": 150, "achieved_at": t2},
            ],
        )
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["score"] == 200  # t3 is newest
        assert data[1]["score"] == 150  # t2
        assert data[2]["score"] == 100  # t1 is oldest

    def test_multi_game_aggregation_correct_slug_title(self, client: TestClient, test_db):
        # TC2: Scores across 2 games; each row carries the join'd game_slug and game_title.
        t1 = datetime(2024, 1, 1, 10, 0, 0)
        t2 = datetime(2024, 1, 2, 10, 0, 0)
        _insert_scores(
            test_db,
            "alice",
            1,
            [
                {"game_slug": "super-mario-bros", "score": 100, "achieved_at": t1},
                {"game_slug": "tetris", "score": 200, "achieved_at": t2},
            ],
        )
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        # Newest first: tetris (t2) before super-mario-bros (t1)
        assert data[0]["game_slug"] == "tetris"
        assert data[0]["game_title"] == "Tetris"
        assert data[1]["game_slug"] == "super-mario-bros"
        assert data[1]["game_title"] == "Super Mario Bros."

    def test_default_limit_truncates_to_10(self, client: TestClient, test_db):
        # TC3: Without ?limit=, default of 10 is applied; 10 newest of 12 are returned.
        base_time = datetime(2024, 1, 1, 10, 0, 0)
        _insert_scores(
            test_db,
            "alice",
            1,
            [
                {
                    "game_slug": "super-mario-bros",
                    "score": i * 100,
                    "achieved_at": base_time + timedelta(hours=i),
                }
                for i in range(12)
            ],
        )
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        assert data[0]["score"] == 1100  # i=11 is newest

    def test_explicit_limit_truncates_after_ordering(self, client: TestClient, test_db):
        # TC4: ?limit=3 returns the 3 newest rows, not 3 oldest or 3 arbitrary rows.
        base_time = datetime(2024, 1, 1, 10, 0, 0)
        _insert_scores(
            test_db,
            "alice",
            1,
            [
                {
                    "game_slug": "super-mario-bros",
                    "score": i * 100,
                    "achieved_at": base_time + timedelta(hours=i),
                }
                for i in range(5)
            ],
        )
        resp = client.get("/users/alice/scores?limit=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["score"] == 400  # i=4, newest
        assert data[1]["score"] == 300  # i=3
        assert data[2]["score"] == 200  # i=2

    def test_username_isolation(self, client: TestClient):
        # TC5: GET /users/alice/scores returns only alice's rows, not bob's.
        alice_token = make_token(user_id=1, username="alice")
        bob_token = make_token(user_id=2, username="bob")
        client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": 100},
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": 999},
            headers={"Authorization": f"Bearer {bob_token}"},
        )
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["score"] == 100

    def test_unknown_user_returns_200_empty_list(self, client: TestClient):
        # TC6: A username with no scores returns 200 + [], never 404.
        resp = client.get("/users/nobody-exists/scores")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_response_shape_is_exact(self, client: TestClient):
        # TC7: Each row contains exactly {game_slug, game_title, score, achieved_at}.
        token = make_token(user_id=1, username="alice")
        client.post(
            "/scores",
            json={"game_slug": "super-mario-bros", "score": 500},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert set(data[0].keys()) == {"game_slug", "game_title", "score", "achieved_at"}

    def test_public_access_no_auth_header_required(self, client: TestClient):
        # TC8: Route is public; no Authorization header is needed.
        resp = client.get("/users/alice/scores")
        assert resp.status_code == 200
