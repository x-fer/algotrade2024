from fastapi import APIRouter

# GAME PATHS

# /game/list?team_secret=
# /game/[id]/time?team_secret=


router = APIRouter()


@router.get("/game/list")
async def game_list():
    return {"message": "Hello World"}