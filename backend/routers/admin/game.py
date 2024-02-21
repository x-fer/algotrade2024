from datetime import datetime
from fastapi import APIRouter, HTTPException
from model import Game, Datasets, Player
from game.bots import Bots
from pydantic import BaseModel
from datetime import datetime
from logger import logger

# GAME PATHS

# POST	/admin/game/create	{"game_name": [name], "start_time": [time], "bots": [[id], [id], [id]], "dataset": [id], "tick_time": [tick_time], "length": [len], "contest": [bool]} // contest brani delete i ogranicava pravljenje playera na 1	{"game_id":[game_id]}
# GET	/admin/game/list	-	[{"start_time": TIME, "game_id": game_id, "contest": bool}]
# GET	/admin/game/[id]/delete	-	{"success": [success]}
# POST	/admin/game/[id]/edit	{}	{"success": [success]}


router = APIRouter()


class CreateGameParams(BaseModel):
    game_name: str
    contest: bool
    bots: str
    dataset: str
    start_time: datetime
    total_ticks: int
    tick_time: int


class EditGameParams(BaseModel):
    game_name: str
    contest: bool
    bots: str
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int


@router.post("/game/create")
async def game_create(params: CreateGameParams):
    Bots.validate_string(params.bots)

    try:
        Datasets.get(params.dataset_id)
    except:
        raise HTTPException(400, "Dataset does not exist")

    Datasets.validate_ticks(params.dataset_id, params.total_ticks)

    if params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.create(
        game_name=params.game_name,
        is_contest=params.contest,
        bots=params.bots,
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
    return {"message": "success"}


@router.post("/game/{game_id}/edit")
async def game_edit(game_id: int, params: EditGameParams):
    if params.bots is not None:
        Bots.validate_string(params.bots)  # a:10;b:10;c:10;d:10

    if params.dataset is not None:
        Datasets.validate_string(params.dataset)

    if params.total_ticks is not None:
        dataset = await Game.get(game_id=game_id)
        dataset = dataset.dataset

        if params.dataset is not None:
            dataset = params.dataset

        Datasets.validate_ticks(dataset, params.total_ticks)

    if params.start_time is not None and params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.update(
        game_id=game_id,
        **params.dict(exclude_unset=True)
    )

    return {"message": "success"}
