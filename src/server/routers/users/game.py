from fastapi import APIRouter
from db import Game

# GAME PATHS

# /game/list?team_secret=
# /game/[id]/time?team_secret=


router = APIRouter()


@router.get("/game/list")
async def game_list():
    games = await Game.list()
    return {"games": games}