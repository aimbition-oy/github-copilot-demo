"""Games router: browse the game catalogue."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Game
from app.schemas import GameResponse

router = APIRouter(tags=["games"])


@router.get("/games", response_model=list[GameResponse])
def list_games(db: Session = Depends(get_db)) -> list[Game]:
    """Return all games in the catalogue."""
    return db.query(Game).all()


@router.get("/games/{slug}", response_model=GameResponse)
def get_game(slug: str, db: Session = Depends(get_db)) -> Game:
    """Return a single game by its slug, or 404 if not found."""
    game = db.query(Game).filter(Game.slug == slug).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game
