from fastapi import APIRouter, Depends, HTTPException, Query
from db import migration
from . import dataset, bot, team, game
from config import config


def admin_dep(admin_secret: str = Query(description="Admin secret", default=None)):
    if admin_secret is None:
        raise HTTPException(status_code=403, detail="Missing admin_secret")
    if admin_secret != config["admin"]["secret"]:
        raise HTTPException(status_code=403, detail="Invalid admin_secret")


router = APIRouter(dependencies=[Depends(admin_dep)], include_in_schema=False)


@router.get("/migrate")
async def migrate():
    await migration.drop_tables()
    await migration.run_migrations()
    return {"message": "succesfully migrated database"}


router.include_router(dataset.router)
router.include_router(bot.router)
router.include_router(game.router)
router.include_router(team.router)
