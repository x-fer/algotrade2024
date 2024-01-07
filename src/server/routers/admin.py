import string
import random
from datetime import datetime
from fastapi import APIRouter
from db import database, Game, Team, migration, Bots, Datasets
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


@router.get("/migrate")
async def migrate():
    await migration.drop_tables(database)
    await migration.run_migrations(database)
    return {"message": "succesfully migrated database"}

# GAME PATHS

# POST	/admin/game/create	{"game_name": [name], "start_time": [time], "bots": [[id], [id], [id]], "dataset": [id], "tick_time": [tick_time], "length": [len], "contest": [bool]} // contest brani delete i ogranicava pravljenje playera na 1	{"game_id":[game_id]}
# GET	/admin/game/list	-	[{"start_time": TIME, "game_id": game_id, "contest": bool}]
# GET	/admin/game/[id]/delete	-	{"success": [success]}
# POST	/admin/game/[id]/edit	{}	{"success": [success]}


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

import random
import string


class CreateTeam(BaseModel):
    team_name: str


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    # TODO: Nemoguce da se dvaput stvori tim s istim idjem...
    return ''.join(random.choice(chars) for _ in range(size))


@router.post("/team/create")
async def team_create(params: CreateTeam):
    team_secret = id_generator()
    return await Team.create(team_name=params.team_name, team_secret=team_secret)


@router.get("/team/list")
async def team_list():
    return await Team.list()


@router.get("/team/{team_id}/delete")
async def team_delete(team_id: int):
    return await Team.delete(team_id=team_id)
