import string
import random
from fastapi import APIRouter
from db import Team
from pydantic import BaseModel

# TEAM PATHS

# POST	/admin/team/create	{"name": [name]}	{"team_id":[team_id], "team_secret": [team_secret]}
# GET	/admin/team/list	-	[{}, {}, {}]
# GET	/admin/team/[team_id]/delete	-	{"success": [success]}

router = APIRouter()


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
