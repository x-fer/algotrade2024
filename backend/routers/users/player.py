from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from db import database
from model import Player, Team
from config import config
from model.game import Game
from model.order import Order
from .dependencies import game_dep, player_dep, check_game_active_dep, team_dep
from routers.model import SuccessfulResponse


router = APIRouter(dependencies=[])


class PlayerData(BaseModel):
    player_id: int
    player_name: str
    game_id: int = Field(..., description="game in which this player exists")
    energy_price: int = Field(..., description="energy price set by the player")
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


@router.get(
    "/game/{game_id}/player/list", summary="Get list of your players in the game"
)
async def player_list(
    game: Game = Depends(game_dep), team: Team = Depends(team_dep)
) -> List[PlayerData]:
    players = await Player.list(
        game_id=game.game_id, team_id=team.team_id, is_active=True
    )
    return players


class PlayerCreate(BaseModel):
    player_name: str = None


class PlayerCreateResponse(BaseModel):
    player_id: int
    player_name: str


@router.post("/game/{game_id}/player/create", summary="Create a player in the game")
async def player_create(
    game: Game = Depends(game_dep),
    team: Team = Depends(team_dep),
    player_create: PlayerCreate | None | dict = None,
) -> PlayerCreateResponse:
    f"""
    Create a player in the game with a given name.
    Name is chosen automatically if left blank.

    **Important:**
    - You can have at most one player in contest mode
    - In normal game you can have at most {config["player"]["max_players_per_team"]}
    """
    async with database.transaction():
        team_players = await Player.count(
            game_id=game.game_id, team_id=team.team_id, is_active=True
        )
        if game.is_contest and team_players >= 1:
            raise HTTPException(
                400, "Only one player per team can be created in contest mode"
            )

        if team_players >= config["player"]["max_players_per_team"]:
            raise HTTPException(400, "Maximum number of players per team reached")

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
            money=starting_money*10000,
        )

    return PlayerCreateResponse(player_id=player_id, player_name=player_name)


@router.get(
    "/game/{game_id}/player/{player_id}",
    dependencies=[Depends(check_game_active_dep)],
    summary="Get player data",
)
async def player_get(player: Player = Depends(player_dep)) -> PlayerData:
    return await Player.get(player_id=player.player_id)


@router.get("/game/{game_id}/player/{player_id}/delete", summary="Delete the player")
async def player_delete(
    game: Game = Depends(game_dep), player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    """
    Delete the player you own. You can only delete players in normal
    games, not in contest mode.
    """
    if game.is_contest:
        raise HTTPException(400, "Players cannot be deleted in contest mode")

    await Player.update(player_id=player.player_id, is_active=False)
    return SuccessfulResponse()


class PlayerNetWorth(BaseModel):
    plants_owned: dict[str, dict[str, int]] = Field(..., description="players networth based only on power plants")
    money: int
    resources: dict[str, dict[str, int]] = Field(..., description="players networth based on resources prices on the market")
    total: int = Field(..., description="total players networth. this is your score in competition rounds!")


@router.get(
    "/game/{game_id}/player/{player_id}/networth",
    summary="Get networth of your player in current market",
)
async def player_net_worth(
    player: Player = Depends(player_dep), game: Game = Depends(game_dep)
) -> PlayerNetWorth:
    """
    Calculates the networth of your player based on owned power plants,
    money and resources owned. Resources are priced at current market data.

    You don't have to sell your resources at the end of the game to have
    bigger networth!

    **Important**: This value is used at the end of competition rounds for scoring.
    """
    if game.current_tick == 0:
        raise HTTPException(
            400, "Game has not started yet or first tick has not been processed"
        )

    return await player.get_networth(game)


@router.get(
    "/game/{game_id}/player/{player_id}/reset",
    summary="Reset the player to starting resources",
)
async def player_reset(
    game: Game = Depends(game_dep),
    team: Team = Depends(team_dep),
    player: Player = Depends(player_dep),
) -> SuccessfulResponse:
    """
    Reset the player you own. This sets its money, resources
    and owned power plants to starting setting.

    You can only reset players in normal games, not in contest mode.
    """
    if game.is_contest:
        raise HTTPException(400, "Players cannot be reset in contest mode")

    fields = {
        x: 0
        for x in Player.__dataclass_fields__.keys()
        if x
        not in [
            "player_id",
            "player_name",
            "game_id",
            "team_id",
            "is_active",
            "is_bot",
            "table_name",
        ]
    }
    fields["money"] = config["player"]["starting_money"]
    fields["energy_price"] = 1e9

    async with database.transaction():
        await Player.update(player_id=player.player_id, **fields)
        await Order.cancel_player_orders(player_id=player.player_id)

    return SuccessfulResponse()
