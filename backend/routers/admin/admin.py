from fastapi import APIRouter, Depends, HTTPException, Query
from db import migration, limiter
from . import dataset, team, game, player
from config import config
from routers.model import SuccessfulResponse


def admin_dep(admin_secret: str = Query(description="Admin secret", default=None)):
    if admin_secret is None:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if admin_secret != config["admin"]["secret"]:
        raise HTTPException(status_code=403, detail="Unauthorized")


router = APIRouter(dependencies=[Depends(admin_dep)], include_in_schema=False)


@router.get("/migrate")
@limiter.exempt
async def migrate() -> SuccessfulResponse:
    await migration.drop_tables()
    await migration.run_migrations()
    return SuccessfulResponse()


router.include_router(player.router)
router.include_router(dataset.router)
router.include_router(game.router)
router.include_router(team.router)
