from fastapi import APIRouter, Depends
from db import Player
from routers.users.dependencies import team_id

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter()


@router.get("/game/{game_id}/player/list")
async def player_list(game_id: int):
    players = await Player.list(game_id=game_id)
    return {"players": players}


@router.get("/game/{game_id}/player/create")
async def player_list(game_id: int, team_id: int=Depends(team_id)):
    print("KEY", team_id)
    players = await Player.list(game_id=game_id, team_id=team_id)
    return {"players": players}
