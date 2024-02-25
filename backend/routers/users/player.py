from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from db import database
from model import Player, Team
from config import config
from model.game import Game
from .dependencies import game_dep, player_dep, check_game_active_dep, team_dep

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter(dependencies=[])


class PlayerListResponseItem(BaseModel):
    player_id: int
    player_name: str


@router.get("/game/{game_id}/player/list")
async def player_list(game: Game = Depends(game_dep),
                      team: Team = Depends(team_dep)) -> List[PlayerListResponseItem]:
    players = await Player.list(game_id=game.game_id, team_id=team.team_id, is_active=True)
    return [{
        "player_id": x.player_id,
        "player_name": x.player_name,
    } for x in players]


class PlayerCreate(BaseModel):
    player_name: str = None


class PlayerResponse(BaseModel):
    player_id: int
    player_name: str


@router.post("/game/{game_id}/player/create")
async def player_create(game: Game = Depends(game_dep),
                        team: Team = Depends(team_dep),
                        player_create: PlayerCreate | None | dict = None) -> PlayerResponse:
    async with database.transaction():
        team_id = team.team_id
        game_id = game.game_id

        player_name = player_create.player_name
        if player_create is None or player_create.player_name is None:
            team_players_len = await Player.count(team_id=team_id, game_id=game_id)
            player_name = f"{team.team_name}_{team_players_len}"

        player_id = await Player.create(game_id=game_id, team_id=team_id, player_name=player_name, money=config["player"]["starting_money"])

    return {"player_id": player_id, "player_name": player_name}


@router.get("/game/{game_id}/player/{player_id}", dependencies=[Depends(check_game_active_dep)])
async def player_get(game: Game = Depends(game_dep),
                     player: Player = Depends(player_dep)) -> Player:
    return await Player.get(player_id=player.player_id)


class PlayerDeleteResponse(BaseModel):
    successfull: bool = False


@router.get("/game/{game_id}/player/{player_id}/delete")
async def player_delete(game: Game = Depends(game_dep),
                        player: Player = Depends(player_dep)) -> PlayerDeleteResponse:
    await Player.update(player_id=player.player_id, is_active=False)
    return {"successfull": True}
