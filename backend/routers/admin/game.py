from datetime import datetime
from fastapi import APIRouter, HTTPException
from model import Game, Datasets, Player
from game.bots import Bots
from pydantic import BaseModel
from datetime import datetime
from logger import logger

router = APIRouter()


class CreateGameParams(BaseModel):
    game_name: str
    contest: bool
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int


class EditGameParams(BaseModel):
    game_name: str | None
    contest: bool | None
    dataset_id: int | None
    start_time: datetime | None
    total_ticks: int | None
    tick_time: int | None


@router.post("/game/create")
async def game_create(params: CreateGameParams):
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

    return {"message": "success"}


@router.get("/game/list")
async def game_list():
    games = await Game.list()
    return {"games": games}


@router.get("/game/{game_id}/player/list")
async def player_list(game_id: int):
    players = await Player.list(game_id=game_id)
    return {"players": players}


@router.get("/game/{game_id}/delete")
async def game_delete(game_id: int):
    # TODO ne baca exception ako je vec zavrsena
    await Game.update(game_id=game_id, is_finished=True)
    return {"success": True}


@router.post("/game/{game_id}/edit")
async def game_edit(game_id: int, params: EditGameParams):
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

    return {"success": True}
