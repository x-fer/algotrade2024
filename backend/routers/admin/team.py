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
def team_create(params: CreateTeam) -> Team:
    team_secret = id_generator()
    team_name = params.team_name

    # team_id = await Team.create(team_name=team_name, team_secret=team_secret)
    t = Team(team_name=team_name, team_secret=team_secret)
    t.save()

    return t


@router.get("/team/list")
@limiter.exempt
def team_list() -> List[Team]:
    return Team.find().all()


@router.post("/team/{team_id}/delete")
@limiter.exempt
def team_delete(team_id: str) -> SuccessfulResponse:
    # team_id = await Team.delete(team_id=team_id)

    if Team.find(Team.team_id == team_id).count() == 0:
        raise HTTPException(status_code=400, detail="Team not found")

    Team.find(Team.team_id == team_id).delete()

    return SuccessfulResponse()
