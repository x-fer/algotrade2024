from fastapi import APIRouter, Depends
from db import limiter
from model.team import Team
from model import Game, Player
from routers.model import SuccessfulResponse
from routers.users.dependencies import game_dep, player_dep


router = APIRouter()


@router.get("/game/{game_id}/player/{player_id}/delete")
@limiter.exempt
async def player_delete(game: Game = Depends(game_dep),
                        player: Player = Depends(player_dep)) -> SuccessfulResponse:
    await Player.update(player_id=player.player_id, is_active=False)
    if game.is_contest:
        return SuccessfulResponse(message=f"Warning: This game is a contest game! Deleted player {player.player_id}.")
    return SuccessfulResponse()
