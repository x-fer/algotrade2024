import dataclasses
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import database
from model import Player, PowerPlantType
from .dependencies import player
from config import config

# POWER_PLANT PATHS

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
    player = await Player.get(player_id=player_id)

    return {
        x.name: {
            "plants_powered": player[x.name.lower() + "_plants_powered"],
            "plants_owned": player[x.name.lower() + "_plants_owned"],
            "next_price": x.get_plant_price(player[x.name.lower() + "_plants_owned"]),
            "sell_price": round(x.get_plant_price(player[x.name.lower() + "_plants_owned"]) * config["power_plant"]["sell_coeff"]),
        }
        for x in PowerPlantType
    }


class PlantBuySell(BaseModel):
    type: PowerPlantType


@router.post("/game/{game_id}/player/{player_id}/plant/buy")
async def buy_plant(player_id: int, plant: PlantBuySell):
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_price = type.get_plant_price(plant_count)

        if player.money < plant_price:
            raise HTTPException(status_code=400, detail="Not enough money")

        await Player.update(player_id=player_id, money=player.money - plant_price)
        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_owned": plant_count + 1})


@router.post("/game/{game_id}/player/{player_id}/plant/sell")
async def sell_plant(player_id: int, plant: PlantBuySell):
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_price = type.get_plant_price(plant_count)

        await Player.update(player_id=player_id, money=player.money + round(plant_price * config["power_plant"]["sell_coeff"]))
        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_owned": plant_count - 1})


class PowerOn(BaseModel):
    number: int


@router.post("/game/{game_id}/player/{player_id}/plant/on")
async def turn_on(player_id: int, plant: PowerOn):
    async with database.transaction():
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]

        if plant_count < plant.number or plant.number < 0:
            raise HTTPException(
                status_code=400, detail="Not enough plants or invalid number")

        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_powered": plant.number})
