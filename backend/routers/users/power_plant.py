from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from db import database
from model import Player, PowerPlantType
from .dependencies import check_game_active_dep, player_dep
from config import config
from typing import Dict
from routers.model import SuccessfulResponse


router = APIRouter(dependencies=[Depends(check_game_active_dep)])


class PowerPlantData(BaseModel):
    plants_powered: int = Field(..., description="number of plants of this type powered on")
    plants_owned: int = Field(..., description="number of plants of this type owned by the player")
    next_price: int = Field(..., description="price at which you can buy your next power plant of this type")
    sell_price: int = Field(..., description="price at which you can sell this power plant")


@router.get(
    "/game/{game_id}/player/{player_id}/plant/list", summary="List power plants you own"
)
async def list_plants(
    player: Player = Depends(player_dep),
) -> Dict[str, PowerPlantData]:
    """
    Returns number of power plants you own for each resource,
    and number of them that are turned on.

    Also returns the price at which you can buy another one, and
    the price at which you can sell your last one.

    Prices are calculated with special formula that is bigger when
    you own more power plants.

    The price at which you sell the power plant is **lower** than buying
    price, so don't buy power plants if you don't mean it!
    """
    return {
        x.name: PowerPlantData(
            plants_powered=player[x.name.lower() + "_plants_powered"],
            plants_owned=player[x.name.lower() + "_plants_owned"],
            next_price=x.get_plant_price(player[x.name.lower() + "_plants_owned"]),
            sell_price=round(
                x.get_plant_price(player[x.name.lower() + "_plants_owned"])
                * config["power_plant"]["sell_coeff"]
            ),
        )
        for x in PowerPlantType
    }


class PowerPlantTypeData(BaseModel):
    type: PowerPlantType


@router.post(
    "/game/{game_id}/player/{player_id}/plant/buy", summary="Buy another power plant"
)
async def buy_plant(
    plant: PowerPlantTypeData, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    """
    Each power plant you buy is more expensive than your last one.
    """
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_price = type.get_plant_price(plant_count)

        if player.money < plant_price:
            raise HTTPException(status_code=400, detail="Not enough money")

        await Player.update(player_id=player_id, money=player.money - plant_price)
        await Player.update(
            player_id=player_id,
            **{type.name.lower() + "_plants_owned": plant_count + 1},
        )
    return SuccessfulResponse()


@router.post(
    "/game/{game_id}/player/{player_id}/plant/sell",
    summary="Sell your last power plant",
)
async def sell_plant(
    plant: PowerPlantTypeData, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    f"""
    Power plants are sold at {config["power_plant"]["sell_coeff"]} of their original value.
    """
    type = PowerPlantType(plant.type)

    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        plant_count = player[type.name.lower() + "_plants_owned"]
        plant_powered = player[type.name.lower() + "_plants_powered"]

        if plant_count <= 0:
            raise HTTPException(status_code=400, detail="No plants to sell")

        await Player.update(
            player_id=player_id,
            money=player.money + type.get_sell_price(plant_count),
            **{
                type.name.lower() + "_plants_owned": plant_count - 1,
                type.name.lower() + "_plants_powered": max(
                    0, min(plant_count - 1, plant_powered)
                ),
            },
        )
    return SuccessfulResponse()


class PowerOn(BaseModel):
    type: PowerPlantType
    number: int = Field(..., description="total number of plants of this type you want to have powered on. 0 to turn them all off.")


@router.post(
    "/game/{game_id}/player/{player_id}/plant/on",
    summary="Turn on number of power plants",
)
async def turn_on(
    plant: PowerOn, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    async with database.transaction():
        player_id = player.player_id
        player = await Player.get(player_id=player_id)
        type = PowerPlantType(plant.type)
        plant_count = player[type.name.lower() + "_plants_owned"]

        if plant_count < plant.number or plant.number < 0:
            raise HTTPException(
                status_code=400, detail="Not enough plants or invalid number"
            )

        await Player.update(
            player_id=player_id, **{type.name.lower() + "_plants_powered": plant.number}
        )
    return SuccessfulResponse()
