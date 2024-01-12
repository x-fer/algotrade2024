from fastapi import HTTPException, Query, Depends
from db import Team, Player, PowerPlant


async def team_id(team_secret: str = Query(..., description="Team secret")) -> int:
    try:
        return (await Team.get(team_secret=team_secret)).team_id
    except:
        raise HTTPException(status_code=403, detail="Invalid team_secret")


async def player(game_id: int, player_id: int, team_id: int=Depends(team_id)) -> Player:
    try:
        player = await Player.get(player_id=player_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid player_id")
    if player.team_id != team_id: raise HTTPException(403, "This player doesn't belong to your team")
    if player.game_id != game_id: raise HTTPException(400, f"This player is in game {player.game_id}")
    if player.is_active == False: raise HTTPException(400, f"This player is inactive")
    return player


async def power_plant(power_plant_id: int, player: Player=Depends(player)) -> PowerPlant:
    try:
        power_plant = await PowerPlant.get(power_plant_id=power_plant_id)
    except:
        raise HTTPException(status_code=403, detail="Invalid power_plant_id")
    if power_plant.player_id != player.player_id: raise HTTPException(400, "This power plant doesn't belong to you")
    return power_plant