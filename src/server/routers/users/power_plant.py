from fastapi import APIRouter, Depends, HTTPException
from db import Player, database, Team, PowerPlant
from routers.users.dependencies import team_id, player, power_plant

# /game/[id]/player/[player_id]/plant/prices?team_secret=
# /game/[id]/player/[player_id]/plant/buy?team_secret=
# /game/[id]/player/[player_id]/plant/[plant_id]/sell?team_secret=
# /game/[id]/player/[player_id]/plant/[plant_id]/on?team_secret=
# /game/[id]/player/[player_id]/plant/[plant_id]/off?team_secret=
# /game/[id]/player/[player_id]/plant/[plant_id]/state?team_secret=
# /game/[id]/player/[player_id]/plant/list?team_secret=
# /game/[id]/player/[player_id]/state


router = APIRouter(dependencies=[Depends(player)])


@router.get("/game/{game_id}/player/{player_id}/plant/list")
async def list_plants(player_id: int):
    return {"plants": await PowerPlant.list(player_id=player_id)}


@router.get("/game/{game_id}/player/{player_id}/plant/buy")
async def buy_plant():
    return {"TODO": "TODO"}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/sell")
async def sell_plant(power_plant: PowerPlant=Depends(power_plant)):
    return {"TODO": "TODO"}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/on")
async def turn_on(power_plant: PowerPlant=Depends(power_plant)):
    return {"TODO": "TODO"}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/off")
async def turn_off(power_plant: PowerPlant=Depends(power_plant)):
    return {"TODO": "TODO"}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}")
async def get_plant(power_plant: PowerPlant=Depends(power_plant)):
    return {"power_plant": power_plant}
