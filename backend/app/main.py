"""FastAPI application entry point for the arcade backend."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, HTTPException
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db, init_db
from app.models import Score
from app.routers.games import router as games_router
from app.routers.scores import router as scores_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown tasks."""
    init_db()
    yield


settings = get_settings()

app = FastAPI(title="Arcade Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router)
app.include_router(scores_router)
app.include_router(users_router)


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


# Test router is always registered; the handler guards with the runtime setting so
# that dependency overrides in the test suite work correctly.
_test_router = APIRouter(prefix="/test", tags=["test"])


@_test_router.delete("/scores")
def delete_all_scores(
    db: Session = Depends(get_db),
    cfg: Settings = Depends(get_settings),
) -> dict:
    """Delete all score rows. Only available when ENABLE_TEST_ENDPOINTS=true."""
    if not cfg.enable_test_endpoints:
        raise HTTPException(status_code=404, detail="Not found")
    deleted = db.query(Score).delete()
    db.commit()
    return {"deleted": deleted}


app.include_router(_test_router)
