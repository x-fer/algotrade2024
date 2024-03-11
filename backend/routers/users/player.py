from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import database
from model import Player, Team, PowerPlantType, DatasetData, Resource
from config import config
from model.game import Game
from .dependencies import game_dep, player_dep, check_game_active_dep, team_dep
from routers.model import SuccessfulResponse


router = APIRouter(dependencies=[])


class PlayerData(BaseModel):
    player_id: int
    player_name: str
    game_id: int
    energy_price: int
    money: int

    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int

    coal_plants_owned: int
    uranium_plants_owned: int
    biomass_plants_owned: int
    gas_plants_owned: int
    oil_plants_owned: int
    geothermal_plants_owned: int
    wind_plants_owned: int
    solar_plants_owned: int
    hydro_plants_owned: int

    coal_plants_powered: int
    uranium_plants_powered: int
    biomass_plants_powered: int
    gas_plants_powered: int
    oil_plants_powered: int
    geothermal_plants_powered: int
    wind_plants_powered: int
    solar_plants_powered: int
    hydro_plants_powered: int


@router.get("/game/{game_id}/player/list")
async def player_list(game: Game = Depends(game_dep),
                      team: Team = Depends(team_dep)) -> List[PlayerData]:
    players = await Player.list(game_id=game.game_id, team_id=team.team_id, is_active=True)
    return players


class PlayerCreate(BaseModel):
    player_name: str = None


class PlayerCreateResponse(BaseModel):
    player_id: int
    player_name: str


@router.post("/game/{game_id}/player/create")
async def player_create(game: Game = Depends(game_dep),
                        team: Team = Depends(team_dep),
                        player_create: PlayerCreate | None | dict = None) -> PlayerCreateResponse:
    async with database.transaction():
        team_players = await Player.count(
            game_id=game.game_id,
            team_id=team.team_id,
            is_active=True)
        if game.is_contest and team_players >= 1:
            raise HTTPException(
                400, "Only one player per team can be created in contest mode")
        team_id = team.team_id
        game_id = game.game_id

        if player_create is None or player_create.player_name is None:
            player_name = f"{team.team_name}_{team_players}"
        else:
            player_name = player_create.player_name

        starting_money = config["player"]["starting_money"]

        player_id = await Player.create(
            game_id=game_id,
            team_id=team_id,
            player_name=player_name,
            money=starting_money)

    return PlayerCreateResponse(player_id=player_id, player_name=player_name)


@router.get("/game/{game_id}/player/{player_id}", dependencies=[Depends(check_game_active_dep)])
async def player_get(player: Player = Depends(player_dep)) -> PlayerData:
    return await Player.get(player_id=player.player_id)


@router.get("/game/{game_id}/player/{player_id}/delete")
async def player_delete(game: Game = Depends(game_dep),
                        player: Player = Depends(player_dep)) -> SuccessfulResponse:
    if game.is_contest:
        raise HTTPException(
            400, "Players cannot be deleted in contest mode")

    await Player.update(player_id=player.player_id, is_active=False)
    return SuccessfulResponse()


class PlayerNetWorth(BaseModel):
    plants_owned: dict[str, dict[str, int]]
    money: int
    resources: dict[str, dict[str, int]]
    total: int


@router.get("/game/{game_id}/player/{player_id}/net_worth")
async def player_net_worth(player: Player = Depends(player_dep), game: Game = Depends(game_dep)) -> PlayerNetWorth:
    net_worth = {
        "plants_owned": {},
        "money": player.money,
        "resources": {},
        "total": 0
    }

    for type in PowerPlantType:
        value = 0

        for i in range(1, getattr(player, f"{type.lower()}_plants_owned") + 1):
            value += round(type.get_plant_price(i) *
                           config["power_plant"]["sell_coeff"])

        net_worth["plants_owned"][type.lower()] = {
            "owned": getattr(player, f"{type.lower()}_plants_owned"),
            "value_if_sold": value
        }

    data = (await DatasetData.list_by_game_id_where_tick(
        game.dataset_id, game.game_id, game.total_ticks - 1, game.total_ticks - 1))[0]

    for resource in Resource:
        final_price = data[f"{resource.name.lower()}_price"]
        has = getattr(player, resource.name.lower())

        net_worth["resources"][resource.name.lower()] = {
            "final_price": final_price,
            "player_has": has,
            "value": final_price * has
        }

    net_worth["total"] += player.money
    for type in PowerPlantType:
        net_worth["total"] += net_worth["plants_owned"][type.lower()
                                                        ]["value_if_sold"]

    for resource in Resource:
        net_worth["total"] += net_worth["resources"][resource.name.lower()
                                                     ]["value"]

    return net_worth
