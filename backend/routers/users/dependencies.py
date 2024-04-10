from datetime import datetime
from fastapi import HTTPException, Query, Depends
from model import Team, Player, Game
from typing import Tuple
from config import config
from model.order import Order


def team_dep(
    team_secret: str = Query(
        description="Team secret - given to you at the start of the competition.",
        default=None,
    ),
) -> Team:
    if team_secret is None:
        raise HTTPException(status_code=403, detail="Missing team_secret")
    try:
        return Team.find(Team.team_secret==team_secret).first()
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid team_secret")


def game_dep(game_id: str) -> Game:
    try:
        return Game.get(game_id)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid game_id")


def check_game_active_dep(game: Game = Depends(game_dep)) -> None:
    if game.is_finished:
        raise HTTPException(403, "Game is already finished")
    if datetime.now() < game.start_time:
        raise HTTPException(403, "Game has not started yet")


def player_dep(
    player_id: str, game: Game = Depends(game_dep), team: Team = Depends(team_dep)
) -> Player:
    try:
        player = Player.get(player_id)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid player_id")
    if player.team_id != team.team_id:
        raise HTTPException(403, "This player doesn't belong to your team")
    if player.game_id != game.game_id:
        raise HTTPException(400, f"This player is in game {player.game_id}")
    if not player.is_active:
        raise HTTPException(400, "This player is inactive or already has been deleted")
    return player


def order_dep(order_id: str, game: Game = Depends(game_dep)):
    try:
        order = Order.get(order_id)
    except Exception:
        raise HTTPException(400, "Invalid order_id")
    if game.game_id != order.game_id:
        raise HTTPException(400, f"This order belongs to game {game.game_id}")
    # TODO: dozvoliti da se vidi od drugih playera?
    return order


tick_description = "Enter negative number for relative tick e.g. -5 for current_tick-5. Leave empty for last tick."


def start_end_tick_dep(
    game: Game = Depends(game_dep),
    start_tick: int = Query(
        default=None,
        description=f"Starting tick for this query. {tick_description}",
    ),
    end_tick: int = Query(
        default=None,
        description=f"End tick for this query. {tick_description}",
    ),
) -> Tuple[int, int]:
    if start_tick is None and end_tick is None:
        current_tick = game.current_tick - 1
        start_tick = current_tick
        end_tick = current_tick
    if start_tick is None:
        start_tick = end_tick
    if end_tick is None:
        end_tick = start_tick

    if start_tick < 0:
        start_tick = max(0, game.current_tick + start_tick)
    if end_tick < 0:
        end_tick = max(0, game.current_tick + end_tick)

    if game.current_tick == 0:
        raise HTTPException(
            status_code=400,
            detail="Game just started (it is tick=0), no data to return",
        )

    if start_tick < 0 or end_tick < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Start ({start_tick}) and end ({end_tick}) tick must both be greater than 0",
        )

    if end_tick < start_tick:
        raise HTTPException(
            status_code=400, detail="End tick must be greater than start tick"
        )

    if start_tick >= game.current_tick:
        raise HTTPException(
            status_code=400,
            detail=f"Start tick must be less than current tick (current_tick={game.current_tick})",
        )

    if end_tick >= game.current_tick:
        raise HTTPException(
            status_code=400,
            detail=f"End tick must be less than current tick (current_tick={game.current_tick})",
        )

    max_ticks_in_request = config["dataset"]["max_ticks_in_request"]
    if end_tick - start_tick > max_ticks_in_request:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot request more than {max_ticks_in_request} ticks at once",
        )

    return start_tick, end_tick
