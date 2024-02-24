from fastapi import HTTPException, Query, Depends
from model import Team, Player, Game


async def game_id(game_id: int) -> int:
    try:
        # TODO: add check if game is started
        return (await Game.get(game_id=game_id)).game_id
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
