from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from db import database
from model import Player, Team
from config import config
from .dependencies import team_id, game_id, player, game_id_no_check_time

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter(dependencies=[
    Depends(team_id),
    Depends(game_id_no_check_time)])


class PlayerListResponseItem(BaseModel):
    player_id: int
    player_name: str


@router.get("/game/{game_id}/player/list", tags=["users"])
async def player_list(game_id: int, team_id: int = Depends(team_id)) -> List[PlayerListResponseItem]:
    players = await Player.list(game_id=game_id, team_id=team_id, is_active=True)
    return [{
        "player_id": x.player_id,
        "player_name": x.player_name,
    } for x in players]


class PlayerCreate(BaseModel):
    player_name: str = None


class PlayerResponse(BaseModel):
    player_id: int
    player_name: str


@router.post("/game/{game_id}/player/create", tags=["users"])
async def player_create(game_id: int, team_id: int = Depends(team_id), player_create: PlayerCreate | None | dict = None) -> PlayerResponse:
    async with database.transaction():
        if player_create is None:
            team = await Team.get(team_id=team_id)
            team_players_len = await Player.count(team_id=team_id, game_id=game_id)
            player_name = f"{team.team_name}_{team_players_len}"
        elif player_create.player_name is None:
            team = await Team.get(team_id=team_id)
            team_players_len = await Player.count(team_id=team_id, game_id=game_id)
            player_name = f"{team.team_name}_{team_players_len}"
        else:
            player_name = player_create.player_name

        player_id = await Player.create(game_id=game_id, team_id=team_id, player_name=player_name, money=config["player"]["starting_money"])

    return {"player_id": player_id, "player_name": player_name}


@router.get("/game/{game_id}/player/{player_id}", tags=["users"])
async def player_get(game_id: int, player=Depends(player)) -> Player:
    return await Player.get(player_id=player.player_id)


class PlayerDeleteResponse(BaseModel):
    successfull: bool = False


@router.get("/game/{game_id}/player/{player_id}/delete", tags=["users"])
async def player_delete(game_id: int, player=Depends(player)) -> PlayerDeleteResponse:
    return {"successfull": await Player.update(player_id=player.player_id, is_active=False)}
