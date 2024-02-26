import string
import random
from fastapi import APIRouter, HTTPException
from model import Team
from pydantic import BaseModel
from routers.model import SuccessfulResponse
from typing import List
from db import limiter

router = APIRouter()


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    # TODO: Nemoguce da se dvaput stvori tim s istim idjem...
    return ''.join(random.choice(chars) for _ in range(size))


class CreateTeam(BaseModel):
    team_name: str


@router.post("/team/create")
@limiter.exempt
async def team_create(params: CreateTeam) -> Team:
    team_secret = id_generator()
    team_name = params.team_name
    team_id = await Team.create(team_name=team_name, team_secret=team_secret)
    return Team(
        team_id=team_id,
        team_secret=team_secret,
        team_name=team_name
    )


@router.get("/team/list")
@limiter.exempt
async def team_list() -> List[Team]:
    return await Team.list()


@router.get("/team/{team_id}/delete")
@limiter.exempt
async def team_delete(team_id: int) -> SuccessfulResponse:
    team_id = await Team.delete(team_id=team_id)

    if team_id is None:
        raise HTTPException(status_code=400, detail="Team not found")

    return SuccessfulResponse()
