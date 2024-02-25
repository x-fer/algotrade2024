from datetime import datetime
from fastapi import HTTPException, Query, Depends
from model import Team, Player, Game


async def game_id_no_check_time(game_id: int) -> int:
    try:
        game = await Game.get(game_id=game_id)

        return game_id
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=403, detail="Invalid game_id")


async def game_id(game_id: int) -> int:
    try:
        game = await Game.get(game_id=game_id)
        start_time = game.start_time
        is_finished = game.is_finished

        if is_finished:
            raise HTTPException(403, "Game is already finished")

        if datetime.now() < start_time:
            raise HTTPException(403, "Game has not started yet")

        return game_id
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=403, detail="Invalid game_id")


async def team_id(team_secret: str = Query(description="Team secret", default=None)) -> int:
    if team_secret is None:
        raise HTTPException(status_code=403, detail="Missing team_secret")
    try:
        return (await Team.get(team_secret=team_secret)).team_id
    except:
        raise HTTPException(status_code=403, detail="Invalid team_secret")


async def player(player_id: int, game_id: int = Depends(game_id), team_id: int = Depends(team_id)) -> Player:
    try:
        player = await Player.get(player_id=player_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid player_id")
    if player.team_id != team_id:
        raise HTTPException(403, "This player doesn't belong to your team")
    if player.game_id != game_id:
        raise HTTPException(400, f"This player is in game {player.game_id}")
    if player.is_active == False:
        raise HTTPException(400, f"This player is inactive")
    return player
