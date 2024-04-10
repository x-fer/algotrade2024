from fastapi import APIRouter, Depends
from db import limiter
from model.team import Team
from model import Game, Player
from routers.model import SuccessfulResponse
from routers.users.dependencies import game_dep


router = APIRouter()


@router.get("/game/{game_id}/player/{player_id}/delete")
@limiter.exempt
def player_delete(player_id: str, game: Game = Depends(game_dep)) -> SuccessfulResponse:
    # await Player.update(player_id=player.player_id, is_active=False)

    p = Player.find(Player.pk == player_id).first()

    if p is None:
        return SuccessfulResponse(message=f"Player {player_id} not found.")

    if p.game_id != game.pk:
        return SuccessfulResponse(message=f"Player {player_id} does not belong to game {game.pk}.")

    p.is_active = False
    p.save()

    if game.is_contest:
        return SuccessfulResponse(message=f"Warning: This game is a contest. Player {player_id} will be deleted.")
    return SuccessfulResponse()
