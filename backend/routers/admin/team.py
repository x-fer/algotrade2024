import string
import random
from fastapi import APIRouter, HTTPException
from model import Team
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


@router.post("/team/create", tags=["admin"])
async def team_create(params: CreateTeam):
    team_secret = id_generator()
    team_id = await Team.create(team_name=params.team_name, team_secret=team_secret)

    return {"team_id": team_id, "team_secret": team_secret}


@router.get("/team/list", tags=["admin"])
async def team_list():
    return await Team.list()


@router.get("/team/{team_id}/delete", tags=["admin"])
async def team_delete(team_id: int):
    team_id = await Team.delete(team_id=team_id)

    if team_id is None:
        raise HTTPException(status_code=400, detail="Team not found")

    return {"success": True}
