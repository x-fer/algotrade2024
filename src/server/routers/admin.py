from datetime import datetime
from fastapi import APIRouter
from db import database, Game
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


# GAME PATHS

# POST	/admin/game/create	{"game_name": [name], "start_time": [time], "bots": [[id], [id], [id]], "dataset": [id], "tick_time": [tick_time], "length": [len], "contest": [bool]} // contest brani delete i ogranicava pravljenje playera na 1	{"game_id":[game_id]}
# GET	/admin/game/list	-	[{"start_time": TIME, "game_id": game_id, "contest": bool}]
# GET	/admin/game/[id]/delete	-	{"success": [success]}
# POST	/admin/game/[id]/edit	{}	{"success": [success]}

class CreateGame(BaseModel):
    game_name: str
    start_time: datetime
    bots: list[int]
    dataset: int
    tick_time: int
    length: int
    contest: bool


@router.post("/game/create")
async def game_create(params: CreateGame):
    try:
        # TODO: botovi, dataset, queue, length

        await Game.create(
            game_name=params.game_name,
            start_time=params.start_time,
            queue_id="",
            tick_time=params.tick_time,
            contest=params.contest
        )
    except Exception as e:
        return {"message": str(e)}

    return {"message": "success"}


@router.get("/game/list")
async def game_list():
    return {"message": "Hello World"}


@router.get("/game/{game_id}/delete")
async def game_delete(game_id: int):
    return {"message": "Hello World"}


@router.post("/game/{game_id}/edit")
async def game_edit(game_id: int):
    return {"message": "Hello World"}

# DATASET PATHS

# POST	/admin/dataset/create	{"content": [csv]}	{"id": [id], "success": [success]}
# GET	/admin/dataset/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]
# GET	/admin/dataset/[id]	-	{"content": [csv]}


@router.post("/dataset/create")
async def dataset_create():
    return {"message": "Hello World"}


@router.get("/dataset/list")
async def dataset_list():
    return {"message": "Hello World"}


@router.get("/dataset/{dataset_id}")
async def dataset_get(dataset_id: int):
    return {"message": "Hello World"}

# BOT PATHS

# POST	/admin/bot/create	{"content": [zip]}	{"id": [id], "success": [success]}
# GET	/admin/bot/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]
# GET	/admin/bot/[bot_id]	-	{"content": [zip]}


@router.post("/bot/create")
async def bot_create():
    return {"message": "Hello World"}


@router.get("/bot/list")
async def bot_list():
    return {"message": "Hello World"}


@router.get("/bot/{bot_id}")
async def bot_get(bot_id: int):
    return {"message": "Hello World"}

# TEAM PATHS

# POST	/admin/team/create	{"name": [name]}	{"team_id":[team_id], "team_secret": [team_secret]}
# GET	/admin/team/list	-	[{}, {}, {}]
# GET	/admin/team/[team_id]/delete	-	{"success": [success]}


@router.post("/team/create")
async def team_create():
    return {"message": "Hello World"}


@router.get("/team/list")
async def team_list():
    return {"message": "Hello World"}


@router.get("/team/{team_id}/delete")
async def team_delete(team_id: int):
    return {"message": "Hello World"}
