from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import database
from model import Player, Team
from config import config
from model.game import Game
from .dependencies import game_dep, player_dep, check_game_active_dep, team_dep
from routers.model import SuccesfullResponse


router = APIRouter(dependencies=[])


class PlayerCreateResponse(BaseModel):
    player_id: int
    player_name: str


@router.get("/game/{game_id}/player/list")
async def player_list(game: Game = Depends(game_dep),
                      team: Team = Depends(team_dep)) -> List[PlayerCreateResponse]:
    players = await Player.list(game_id=game.game_id, team_id=team.team_id, is_active=True)
    return [{
        "player_id": x.player_id,
        "player_name": x.player_name,
    } for x in players]


class PlayerCreate(BaseModel):
    player_name: str = None


@router.post("/game/{game_id}/player/create")
async def player_create(game: Game = Depends(game_dep),
                        team: Team = Depends(team_dep),
                        player_create: PlayerCreate | None | dict = None) -> PlayerCreateResponse:
    async with database.transaction():
        team_players = await Player.count(game_id=game.game_id, team_id=team.team_id, is_active=True)
        if game.is_contest and team_players >= 1:
            raise HTTPException(
                400, "Only one player per team can be created in contest mode")
        team_id = team.team_id
        game_id = game.game_id

        if player_create is None or player_create.player_name is None:
            player_name = f"{team.team_name}_{team_players}"
        else:
            player_name = player_create.player_name

        player_id = await Player.create(game_id=game_id, team_id=team_id, player_name=player_name, money=config["player"]["starting_money"])

    return {"player_id": player_id, "player_name": player_name}


class PlayerDataResponse(BaseModel):
    player_id: int
    player_name: str
    game_id: int
    energy_price: int
    money: int

    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int


@router.get("/game/{game_id}/player/{player_id}", dependencies=[Depends(check_game_active_dep)])
async def player_get(player: Player = Depends(player_dep)) -> PlayerDataResponse:
    return await Player.get(player_id=player.player_id)


@router.get("/game/{game_id}/player/{player_id}/delete")
async def player_delete(game: Game = Depends(game_dep),
                        player: Player = Depends(player_dep)) -> SuccesfullResponse:
    if game.is_contest:
        raise HTTPException(
            400, "Players cannot be deleted in contest mode")

    await Player.update(player_id=player.player_id, is_active=False)
    return {"successfull": True}
