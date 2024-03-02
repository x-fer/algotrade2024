from datetime import datetime
from fastapi import HTTPException, Query, Depends
from model import Team, Player, Game
from typing import Tuple
from config import config


async def team_dep(team_secret: str = Query(description="Team secret", default=None)) -> Team:
    if team_secret is None:
        raise HTTPException(status_code=403, detail="Missing team_secret")
    try:
        return await Team.get(team_secret=team_secret)
    except:
        raise HTTPException(status_code=403, detail="Invalid team_secret")


async def game_dep(game_id: int) -> Game:
    try:
        return await Game.get(game_id=game_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid game_id")


async def check_game_active_dep(game: Game = Depends(game_dep)):
    if game.is_finished:
        raise HTTPException(403, "Game is already finished")
    if datetime.now() < game.start_time:
        raise HTTPException(403, "Game has not started yet")


async def player_dep(player_id: int,
                     game: Game = Depends(game_dep),
                     team: Team = Depends(team_dep)) -> Player:
    try:
        player = await Player.get(player_id=player_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid player_id")
    if player.team_id != team.team_id:
        raise HTTPException(403, "This player doesn't belong to your team")
    if player.game_id != game.game_id:
        raise HTTPException(400, f"This player is in game {player.game_id}")
    if player.is_active == False:
        raise HTTPException(
            400, f"This player is inactive or already has been deleted")
    return player


async def start_end_tick_dep(game: Game = Depends(game_dep),
                             start_tick: int = Query(default=None),
                             end_tick: int = Query(default=None)) -> Tuple[int, int]:
    if start_tick is None and end_tick is None:
        current_tick = game.current_tick - 1
        start_tick = current_tick
        end_tick = current_tick
    if start_tick is None:
        start_tick = end_tick
    if end_tick is None:
        end_tick = start_tick

    if game.current_tick == 0:
        raise HTTPException(
            status_code=400, detail="Game just started (it is tick=0), no data to return")

    if start_tick < 0 or end_tick < 0:
        raise HTTPException(
            status_code=400, detail="Start and end tick must both be greater than 0")

    if end_tick < start_tick:
        raise HTTPException(
            status_code=400, detail="End tick must be greater than start tick")

    if start_tick >= game.current_tick:
        raise HTTPException(
            status_code=400, detail=f"Start tick must be less than current tick (current_tick={game.current_tick})")

    if end_tick >= game.current_tick:
        raise HTTPException(
            status_code=400, detail=f"End tick must be less than current tick (current_tick={game.current_tick})")

    max_ticks_in_request = config["dataset"]["max_ticks_in_request"]
    if end_tick - start_tick > max_ticks_in_request:
        raise HTTPException(
            status_code=400, detail=f"Cannot request more than {max_ticks_in_request} ticks at once")

    return start_tick, end_tick
