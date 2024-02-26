from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from db import migration
from . import dataset, team, game
from config import config


def admin_dep(admin_secret: str = Query(description="Admin secret", default=None)):
    if admin_secret is None:
        raise HTTPException(status_code=403, detail="Missing admin_secret")
    if admin_secret != config["admin"]["secret"]:
        raise HTTPException(status_code=403, detail="Invalid admin_secret")


router = APIRouter(dependencies=[Depends(admin_dep)], include_in_schema=False)


class MigrateResponse(BaseModel):
    success: bool


@router.get("/migrate")
async def migrate() -> MigrateResponse:
    await migration.drop_tables()
    await migration.run_migrations()
    return {"success": True}


router.include_router(dataset.router)
router.include_router(game.router)
router.include_router(team.router)
