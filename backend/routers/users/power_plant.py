from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from model import Player, PowerPlantType
from model.power_plant_model import PowerPlantsApiModel, PowerPlantsModel
from .dependencies import check_game_active_dep, player_dep
from config import config
from routers.model import SuccessfulResponse


router = APIRouter(dependencies=[Depends(check_game_active_dep)])


class PowerPlantData(BaseModel):
    power_plants_powered: PowerPlantsApiModel = Field(
        ..., description="Number of plants of this type powered on"
    )
    power_plants_owned: PowerPlantsApiModel = Field(
        ..., description="Number of plants of this type owned by the player"
    )
    buy_price: PowerPlantsApiModel = Field(
        ..., description="Price at which you can buy your next power plant of this type"
    )
    sell_price: PowerPlantsApiModel = Field(
        ..., description="Price at which you can sell this power plant"
    )


@router.get(
    "/game/{game_id}/player/{player_id}/plant/list", summary="List power plants you own"
)
def list_plants(
    player: Player = Depends(player_dep),
) -> PowerPlantData:
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
    buy_price = PowerPlantsModel()
    sell_price = PowerPlantsModel()
    for type in PowerPlantType:
        buy_price[type] = PowerPlantType.get_plant_price(
            type, player.power_plants_owned[type]
        )
        sell_price[type] = PowerPlantType.get_sell_price(
            type, player.power_plants_owned[type]
        )
    return PowerPlantData(
        power_plants_powered=player.power_plants_powered,
        power_plants_owned=player.power_plants_owned,
        buy_price=buy_price,
        sell_price=sell_price,
    )


class PowerPlantTypeData(BaseModel):
    type: PowerPlantType


@router.post(
    "/game/{game_id}/player/{player_id}/plant/buy", summary="Buy another power plant"
)
def buy_plant(
    plant: PowerPlantTypeData, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    """
    Each power plant you buy is more expensive than your last one.
    """
    type = PowerPlantType(plant.type)

    with player.lock():
        player = Player.get(player.player_id)
        plant_count = player.power_plants_owned[type]
        plant_price = type.get_plant_price(plant_count)

        if player.money < plant_price:
            raise HTTPException(status_code=400, detail="Not enough money")

        player.money -= plant_price
        player.power_plants_owned[type] += 1
        player.save()
    return SuccessfulResponse()


@router.post(
    "/game/{game_id}/player/{player_id}/plant/sell",
    summary="Sell your last power plant",
)
def sell_plant(
    plant: PowerPlantTypeData, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    f"""
    Power plants are sold at {config["power_plant"]["sell_coeff"]} of their original value.
    """
    type = PowerPlantType(plant.type)

    with player.lock():
        player = Player.get(player.player_id)
        plant_count = player.power_plants_owned[type]
        plant_powered = player.power_plants_powered[type]
        plant_price = type.get_sell_price(plant_count)

        if plant_count <= 0:
            raise HTTPException(status_code=400, detail="No plants to sell")

        player.money += plant_price
        player.power_plants_owned[type] -= 1
        player.power_plants_powered[type] = max(0, min(plant_count - 1, plant_powered))
        player.save()
    return SuccessfulResponse()


class PowerOn(BaseModel):
    type: PowerPlantType
    number: int = Field(
        ...,
        description="total number of plants of this type you want to have powered on. 0 to turn them all off.",
    )


@router.post(
    "/game/{game_id}/player/{player_id}/plant/on",
    summary="Turn on number of power plants",
)
def turn_on(
    plant: PowerOn, player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    type = PowerPlantType(plant.type)
    if plant.number < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid number of power plants to turn on ({plant.number})",
        )

    with player.lock():
        player = Player.get(player.player_id)
        plant_count = player.power_plants_owned[type]

        if plant_count < plant.number:
            raise HTTPException(status_code=400, detail="Not enough power plants")
        player.power_plants_powered = plant.number
        player.save()
    return SuccessfulResponse()
