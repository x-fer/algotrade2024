from fastapi import APIRouter
from db import database, migration
from routers.admin import dataset, bot, team, game


router = APIRouter()


@router.get("/migrate")
async def migrate():
    await migration.drop_tables(database)
    await migration.run_migrations(database)
    return {"message": "succesfully migrated database"}


router.include_router(dataset.router)
router.include_router(bot.router)
router.include_router(game.router)
router.include_router(team.router)