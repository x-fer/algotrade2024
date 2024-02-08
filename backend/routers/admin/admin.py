from fastapi import APIRouter
from db import migration
from . import dataset, bot, team, game


router = APIRouter()


@router.get("/migrate")
async def migrate():
    await migration.drop_tables()
    await migration.run_migrations()
    return {"message": "succesfully migrated database"}


router.include_router(dataset.router)
router.include_router(bot.router)
router.include_router(game.router)
router.include_router(team.router)
