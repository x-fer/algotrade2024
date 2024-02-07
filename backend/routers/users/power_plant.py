import dataclasses
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import database
from model import Player, PowerPlant, PowerPlantType
from .dependencies import player, power_plant
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


@router.get("/game/{game_id}/player/{player_id}/plant/prices")
async def list_plant_prices(player_id: int):
    return [
        {"type": type,
         "name": type.name,
         "price": type.get_plant_price(player_id=player_id)}
        for type in PowerPlantType
    ]


@router.get("/game/{game_id}/player/{player_id}/plant/list")
async def list_plants(player_id: int):
    return [{**dataclasses.asdict(x),
             "sell_price": round(x.price * config["power_plant_sell_coef"])}
            for x in (await PowerPlant.list(player_id=player_id))]


class PlantBuy(BaseModel):
    type: PowerPlantType


@router.post("/game/{game_id}/player/{player_id}/plant/buy")
async def buy_plant(player_id: int, plant: PlantBuy):
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player_balance = (await Player.get(player_id=player_id)).money
        price = type.get_plant_price(player_id=player_id)

        if player_balance < price:
            raise HTTPException(status_code=400, detail="Not enough money")

        await Player.update(player_id=player_id, money=player_balance - price)

        plant_id = await PowerPlant.create(type=type.value, player_id=player_id, price=price)

    return {"power_plant_id": plant_id}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/sell_price")
async def get_sell_price(power_plant: PowerPlant = Depends(power_plant)):
    sell_coef = config["power_plant_sell_coef"]

    return {"sell_price": round(power_plant.price * sell_coef)}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/sell")
async def sell_plant(power_plant: PowerPlant = Depends(power_plant)):

    sell_coef = config["power_plant_sell_coef"]

    async with database.transaction():
        sell_price = round(power_plant.price * sell_coef)

        balance = (await Player.get(player_id=power_plant.player_id)).money

        await Player.update(player_id=power_plant.player_id, money=balance + sell_price)
        await PowerPlant.delete(power_plant_id=power_plant.power_plant_id)

    return {"sell_price": sell_price, "new_balance": balance + sell_price}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/on")
async def turn_on(power_plant: PowerPlant = Depends(power_plant)):
    async with database.transaction():
        await PowerPlant.update(power_plant_id=power_plant.power_plant_id, is_on=True)
    return {"success": True}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}/off")
async def turn_off(power_plant: PowerPlant = Depends(power_plant)):
    async with database.transaction():
        await PowerPlant.update(power_plant_id=power_plant.power_plant_id, is_on=False)
    return {"success": True}


@router.get("/game/{game_id}/player/{player_id}/plant/{power_plant_id}")
async def get_plant(power_plant: PowerPlant = Depends(power_plant)):
    return await PowerPlant.get(power_plant_id=power_plant.power_plant_id)
