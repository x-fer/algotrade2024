import dataclasses
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import database
from model import Player, PowerPlantType
from .dependencies import check_game_active_dep, player_dep
from config import config


router = APIRouter(dependencies=[Depends(check_game_active_dep)])


class PowerPlantData(BaseModel):
    plants_powered: int
    plants_owned: int
    next_price: int
    sell_price: int


@router.get("/game/{game_id}/player/{player_id}/plant/list")
async def list_plants(player: Player = Depends(player_dep)):
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
async def buy_plant(plant: PlantBuySell, player: Player = Depends(player_dep)):
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_price = type.get_plant_price(plant_count)

        if player.money < plant_price:
            raise HTTPException(status_code=400, detail="Not enough money")

        await Player.update(player_id=player_id, money=player.money - plant_price)
        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_owned": plant_count + 1})


@router.post("/game/{game_id}/player/{player_id}/plant/sell")
async def sell_plant(plant: PlantBuySell, player: Player = Depends(player_dep)):
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_price = type.get_plant_price(plant_count)

        await Player.update(player_id=player_id, money=player.money + round(plant_price * config["power_plant"]["sell_coeff"]))
        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_owned": plant_count - 1})


class PowerOn(BaseModel):
    number: int


@router.post("/game/{game_id}/player/{player_id}/plant/on")
async def turn_on(plant: PowerOn, player: Player = Depends(player_dep)):
    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]

        if plant_count < plant.number or plant.number < 0:
            raise HTTPException(
                status_code=400, detail="Not enough plants or invalid number")

        await Player.update(player_id=player_id, **{type.name.lower() + "_plants_powered": plant.number})
