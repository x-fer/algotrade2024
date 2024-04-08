from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from model import Player, Team
from config import config
from model.game import Game
from model.player import Networth
from model.power_plant_model import PowerPlantsModel, ResourcesModel
from .dependencies import game_dep, player_dep, check_game_active_dep, team_dep
from routers.model import SuccessfulResponse


router = APIRouter(dependencies=[])


class PlayerData(BaseModel):
    player_id: str
    player_name: str
    game_id: int = Field(..., description="game in which this player exists")
    energy_price: int = Field(..., description="energy price set by the player")
    game_id: str

    money: int
    energy: int

    resources: ResourcesModel

    power_plants_owned: PowerPlantsModel
    power_plants_powered: PowerPlantsModel


@router.get(
    "/game/{game_id}/player/list", summary="Get list of your players in the game"
)
def player_list(
    game: Game = Depends(game_dep), team: Team = Depends(team_dep)
) -> List[PlayerData]:
    return Player.find(
        (Player.game_id == game.game_id)
        & (Player.team_id == team.team_id)
        & (Player.is_active == int(True))
    ).all()


class PlayerCreate(BaseModel):
    player_name: str = None


@router.post("/game/{game_id}/player/create", summary="Create a player in the game")
def player_create(
    game: Game = Depends(game_dep),
    team: Team = Depends(team_dep),
    params: PlayerCreate | None = None,
) -> PlayerData:
    f"""
    Create a player in the game with a given name.
    Name is chosen automatically if left blank.

    **Important:**
    - You can have at most one player in contest mode
    - In normal game you can have at most {config["player"]["max_players_per_team"]}
    """
    with team.lock():
        team_players = Player.find(
            (Player.game_id == game.game_id)
            & (Player.team_id == team.team_id)
            & (Player.is_active == int(True))
        ).count()
        if game.is_contest and team_players >= 1:
            raise HTTPException(
                400, "Only one player per team can be created in contest mode"
            )

        if team_players >= config["player"]["max_players_per_team"]:
            raise HTTPException(400, "Maximum number of players per team reached")

        if params is None or params.player_name is None:
            player_name = f"{team.team_name}_{team_players}"
        else:
            player_name = params.player_name

        starting_money = config["player"]["starting_money"]
        return Player(
            game_id=team.team_id,
            team_id=game.game_id,
            player_name=player_name,
            money=starting_money,
        ).save()


@router.get(
    "/game/{game_id}/player/{player_id}",
    summary="Get player data",
)
def player_get(player: Player = Depends(player_dep)) -> PlayerData:
    return player


@router.get("/game/{game_id}/player/{player_id}/delete", summary="Delete the player")
def player_delete(
    game: Game = Depends(game_dep), player: Player = Depends(player_dep)
) -> SuccessfulResponse:
    """
    Delete the player you own. You can only delete players in normal
    games, not in contest mode.
    """
    if game.is_contest:
        raise HTTPException(400, "Players cannot be deleted in contest mode")
    with Player.lock():
        player = Player.get(player.pk)
        if player.is_active:
            raise HTTPException(400, "Cannot delete already deleted player")
        player.update(is_active=False)
    return SuccessfulResponse()


@router.get(
    "/game/{game_id}/player/{player_id}/networth",
    summary="Get networth of your player in current market",
    dependencies=[Depends(check_game_active_dep)],
)
def player_net_worth(
    player: Player = Depends(player_dep), game: Game = Depends(game_dep)
) -> Networth:
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
    return player.get_networth(game)


@router.get(
    "/game/{game_id}/player/{player_id}/reset",
    summary="Reset the player to starting resources",
)
def player_reset(
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

    reset_player = Player(
        pk=player.pk,
        player_name=player.player_name,
        game_id=player.game_id,
        team_id=player.team_id,
    )

    reset_player.money = config["player"]["starting_money"]

    with Player.lock():
        pipe = Player.db().pipeline()
        reset_player.cancel_orders(pipe)
        reset_player.save()
        pipe.execute()

    return SuccessfulResponse()
