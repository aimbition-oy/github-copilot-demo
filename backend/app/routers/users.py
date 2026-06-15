"""Users router: per-player score history."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Game, Score
from app.schemas import PlayerScoreOut

router = APIRouter(tags=["users"])


@router.get("/users/{username}/scores", response_model=list[PlayerScoreOut])
def get_player_scores(
    username: str,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PlayerScoreOut]:
    # No 404 on unknown username — backend has no User table; unknown user yields [].
    rows = (
        db.query(
            Game.slug.label("game_slug"),
            Game.title.label("game_title"),
            Score.score.label("score"),
            Score.achieved_at.label("achieved_at"),
        )
        .select_from(Score)
        .join(Game, Score.game_id == Game.id)
        .filter(Score.username_cached == username)
        .order_by(Score.achieved_at.desc())
        .limit(limit)
        .all()
    )
    return [PlayerScoreOut.model_validate(row, from_attributes=True) for row in rows]
