from enum import Enum
from fastapi import APIRouter


# GAME PATHS


router = APIRouter()


@router.get("/game/{game_id}/market/offer/list")
@router.get("/game/{game_id}/market/offer/list/{tick}")
async def game_list(game_id: int, tick: int = None):
    return {"game_id": game_id, "tick": tick}
