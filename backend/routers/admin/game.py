from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from fastapi import APIRouter, HTTPException
from model import Game, Datasets, Player
from game.bots import Bots
from pydantic import BaseModel
from datetime import datetime
from typing import List
from model.team import Team
from routers.model import SuccessfulResponse
from db import limiter


router = APIRouter()


class CreateGameParams(BaseModel):
    game_name: str
    contest: bool
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int


@router.post("/game/create")
@limiter.exempt
async def game_create(params: CreateGameParams) -> SuccessfulResponse:
    await Datasets.validate_ticks(params.dataset_id, params.total_ticks)

    if params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.create(
        game_name=params.game_name,
        is_contest=params.contest,
        dataset_id=params.dataset_id,
        start_time=params.start_time,
        total_ticks=params.total_ticks,
        tick_time=params.tick_time,
        is_finished=False,
        current_tick=0
    )
    return SuccessfulResponse()


@router.get("/game/list")
@limiter.exempt
async def game_list() -> List[Game]:
    return await Game.list()


@router.get("/game/{game_id}/player/list")
@limiter.exempt
async def player_list(game_id: int) -> List[Player]:
    return await Player.list(game_id=game_id)


@router.post("/game/{game_id}/delete")
@limiter.exempt
async def game_delete(game_id: int) -> SuccessfulResponse:
    # TODO ne baca exception ako je vec zavrsena
    await Game.update(game_id=game_id, is_finished=True)
    return SuccessfulResponse()


class EditGameParams(BaseModel):
    game_name: str | None
    contest: bool | None
    dataset_id: int | None
    start_time: datetime | None
    total_ticks: int | None
    tick_time: int | None


@router.post("/game/{game_id}/edit")
@limiter.exempt
async def game_edit(game_id: int, params: EditGameParams) -> SuccessfulResponse:
    try:
        Bots.parse_string(params.bots)
    except:
        raise HTTPException(400, "Invalid bots string")
    if params.dataset is not None:
        Datasets.validate_string(params.dataset)

    if params.total_ticks is not None:
        dataset = await Game.get(game_id=game_id)
        dataset = dataset.dataset

        if params.dataset is not None:
            dataset = params.dataset

        await Datasets.validate_ticks(dataset, params.total_ticks)

    if params.start_time is not None and params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.update(
        game_id=game_id,
        **params.dict(exclude_unset=True)
    )
    return SuccessfulResponse()


@dataclass
class NetworthData:
    team_id: int
    team_name: str
    player_id: int
    player_name: str
    networth: int


@router.get("/game/{game_id}/networth")
@limiter.exempt
async def game_networth(game_id: int) -> List[NetworthData]:
    game = await Game.get(game_id=game_id)

    if game.current_tick == 0:
        raise HTTPException(
            400, "Game has not started yet or first tick has not been processed")

    players = await Player.list(game_id=game_id)

    team_networths = []

    for player in players:
        team_networths.append({
            "team_id": player.team_id,
            "team_name": (await Team.get(team_id=player.team_id)).team_name,
            "player_id": player.player_id,
            "player_name": player.player_name,
            "networth": (await player.get_networth(game))["total"]
        })

    return team_networths
