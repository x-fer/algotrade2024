from typing import List
from fastapi import APIRouter
from model import Game

# GAME PATHS

# /game/list?team_secret=
# /game/[id]/time?team_secret=


router = APIRouter()


@router.get("/game/list")
async def game_list() -> List[Game]:
    games = await Game.list()
    return games
