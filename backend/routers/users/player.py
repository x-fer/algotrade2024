from fastapi import APIRouter, Depends
from pydantic import BaseModel
from db import database
from model import Player, Team
from config import config
from .dependencies import team_id, game_id, player

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter()


@router.get("/game/{game_id}/player/list", tags=["users"])
async def player_list(game_id: int, team_id: int = Depends(team_id)):
    players = await Player.list(game_id=game_id, team_id=team_id, is_active=True)
    return {"players": players}


class PlayerCreate(BaseModel):
    player_name: str = None


@router.post("/game/{game_id}/player/create", tags=["users"])
async def player_create(game_id: int = Depends(game_id), team_id: int = Depends(team_id), player_name: str = None):
    async with database.transaction():
        if player_name is None:
            team = await Team.get(team_id=team_id)
            team_players_len = await Player.count(team_id=team_id, game_id=game_id)
            player_name = f"{team.team_name}_{team_players_len}"

        player_id = await Player.create(game_id=game_id, team_id=team_id, player_name=player_name, money=config["player"]["starting_money"])
    return {"player_id": player_id}


@router.get("/game/{game_id}/player/{player_id}", tags=["users"])
async def player_get(player=Depends(player)):
    return await Player.get(player_id=player.player_id)


@router.get("/game/{game_id}/player/{player_id}/delete", tags=["users"])
async def player_delete(player=Depends(player)):
    return {"successfull": await Player.update(player_id=player.player_id, is_active=False)}
