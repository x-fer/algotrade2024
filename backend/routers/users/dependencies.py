from datetime import datetime
from fastapi import HTTPException, Query, Depends
from model import Team, Player, Game


async def team(team_secret: str = Query(description="Team secret", default=None)) -> Team:
    if team_secret is None:
        raise HTTPException(status_code=403, detail="Missing team_secret")
    try:
        return await Team.get(team_secret=team_secret)
    except:
        raise HTTPException(status_code=403, detail="Invalid team_secret")


async def game(game_id: int) -> Game:
    try:
        return await Game.get(game_id=game_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid game_id")


async def check_game_active(game: Game = Depends(game)) -> None:
    if game.is_finished:
        raise HTTPException(403, "Game is already finished")
    if datetime.now() < game.start_time:
        raise HTTPException(403, "Game has not started yet")


async def player(player_id: int, game: Game = Depends(game), team: int = Depends(team)) -> Player:
    try:
        player = await Player.get(player_id=player_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid player_id")
    if player.team_id != team.team_id:
        raise HTTPException(403, "This player doesn't belong to your team")
    if player.game_id != game.game_id:
        raise HTTPException(400, f"This player is in game {player.game_id}")
    if player.is_active == False:
        raise HTTPException(400, f"This player is inactive")
    return player
