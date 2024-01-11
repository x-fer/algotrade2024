from fastapi import APIRouter

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter()


@router.get("/game/{game_id}/player/list")
async def bot_list(game_id: int):
    return {"message": "Hello World"}