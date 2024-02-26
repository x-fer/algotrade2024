from fastapi import APIRouter
from db import limiter
from model.team import Team
from routers.model import SuccessfulResponse


router = APIRouter()


@router.get("/team/{team_id}/delete")
@limiter.exempt
async def team_delete(team_id: int) -> SuccessfulResponse:
    await Team.update(team_id=team_id, is_active=False)
    return SuccessfulResponse()
