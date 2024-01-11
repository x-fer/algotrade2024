import string
import random
from datetime import datetime
from fastapi import APIRouter
from db import database, Game, Bots, Datasets
from pydantic import BaseModel
from datetime import datetime

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
    game_name: str | None
    contest: bool | None
    bots: str | None
    dataset: str | None
    start_time: datetime | None
    total_ticks: int | None
    tick_time: int | None


@router.post("/game/create")
async def game_create(params: CreateGameParams):
    # TODO dodati validaciju za botove

    try:
        Bots.validate_string(params.bots)  # a:10;b:10;c:10;d:10
        Datasets.validate_string(params.dataset)
        Datasets.ensure_ticks(params.dataset, params.total_ticks)

        if params.start_time < datetime.now():
            raise Exception("Start time must be in the future")

        await Game.create(
            game_name=params.game_name,
            is_contest=params.contest,
            bots=params.bots,
            dataset=params.dataset,
            start_time=params.start_time,
            total_ticks=params.total_ticks,
            tick_time=params.tick_time,
            is_finished=False,
            current_tick=0
        )

    except Exception as e:
        return {"message": str(e)}

    return {"message": "success"}


@router.get("/game/list")
async def game_list():
    try:
        games = await Game.list()
    except Exception as e:
        return {"message": str(e)}
    print(games)

    return {"games": games}


@router.get("/game/{game_id}/delete")
async def game_delete(game_id: int):
    try:
        # TODO ne baca exception ako je vec zavrsena
        await Game.update(game_id=game_id, is_finished=True)
    except Exception as e:
        return {"message": str(e)}

    return {"message": "success"}


@router.post("/game/{game_id}/edit")
async def game_edit(game_id: int, params: EditGameParams):
    try:
        if params.bots is not None:
            Bots.validate_string(params.bots)  # a:10;b:10;c:10;d:10

        if params.dataset is not None:
            Datasets.validate_string(params.dataset)

        if params.total_ticks is not None:
            dataset = await Game.get(game_id=game_id)
            dataset = dataset.dataset

            if params.dataset is not None:
                dataset = params.dataset

            Datasets.ensure_ticks(dataset, params.total_ticks)

        if params.start_time is not None and params.start_time < datetime.now():
            raise Exception("Start time must be in the future")

        await Game.update(
            game_id=game_id,
            **params.dict(exclude_unset=True)
        )
    except Exception as e:
        return {"message": str(e)}

    return {"message": "success"}