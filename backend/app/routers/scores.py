"""Scores router: submit scores and retrieve leaderboards."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Game, Score
from app.schemas import LeaderboardEntry, ScoreResponse, ScoreSubmitRequest
from app.security import get_current_user

router = APIRouter(tags=["scores"])


@router.post("/scores", response_model=ScoreResponse, status_code=201)
def submit_score(
    body: ScoreSubmitRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Score:
    """Submit a new high score for the authenticated user."""
    game = db.query(Game).filter(Game.slug == body.game_slug).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    score = Score(
        user_id=current_user["user_id"],
        username_cached=current_user["username"],
        game_id=game.id,
        score=body.score,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.get("/games/{slug}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    slug: str,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LeaderboardEntry]:
    """Return the top scores for a game, ordered by score descending."""
    game = db.query(Game).filter(Game.slug == slug).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    rows = (
        db.query(Score)
        .filter(Score.game_id == game.id)
        .order_by(Score.score.desc())
        .limit(limit)
        .all()
    )

    return [
        LeaderboardEntry(
            rank=idx + 1,
            username=row.username_cached,
            score=row.score,
            achieved_at=row.achieved_at,
        )
        for idx, row in enumerate(rows)
    ]
