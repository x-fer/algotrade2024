import pandas as pd
from game.tick import TickData, Ticker
from model import Order, Player, Resource, Game, PowerPlant, PowerPlantType, OrderSide
from game.market import ResourceMarket, EnergyMarket
import pytest

from model.order_types import OrderStatus


@pytest.fixture
def game_id():
    return 1


@pytest.fixture
def game():
    return Game(game_id=1,
                game_name=f"game_{game_id}",
                is_contest=False,
                bots="",
                dataset="",
                start_time=pd.Timestamp.now(),
                total_ticks=1000,
                tick_time=1000,
                )


@pytest.fixture
def team_id():
    return 1


@pytest.fixture
def get_ticker():
    def get_ticker():
        return Ticker()
    return get_ticker


@pytest.fixture
def get_game_data():
    game_id = 0

    def get_game_data(**kwargs) -> Game:
        nonlocal game_id
        game = Game(
            game_id=game_id,
            game_name=f"game_{game_id}",
            is_contest=False,
            bots="",
            dataset="",
            start_time=pd.Timestamp.now(),
            total_ticks=1000,
            tick_time=1000,
            **kwargs
        )
        game_id += 1
        return game
    return get_game_data


@pytest.fixture
def get_tick_data():
    def get_tick_data(**kwargs) -> TickData:
        return TickData(
            game=Game(
                game_id=game_id,
                game_name=f"game_{game_id}",
                is_contest=False,
                bots="",
                dataset="",
                start_time=pd.Timestamp.now(),
                total_ticks=1000,
                tick_time=1000,
            ),
            bots=[],
            **kwargs
        )
    return get_tick_data


@pytest.fixture
def get_player(game_id, team_id):
    player_id = 0

    def get_player(**kwargs) -> Player:
        nonlocal player_id
        player = Player(
            player_id=player_id,
            player_name=f"player_{player_id}",
            team_id=team_id,
            game_id=game_id,
            **kwargs
        )
        player_id += 1
        return player
    return get_player


@pytest.fixture
def get_order():
    order_id = 0

    def get_order(player_id: int, price: int, size: int, order_side: OrderSide, tick: int) -> Order:
        nonlocal order_id
        order = Order(
            order_id=order_id,
            game_id=1,
            player_id=player_id,
            resource=Resource.coal.value,
            price=price,
            tick=tick,
            size=size,
            order_side=order_side,
        )
        order_id += 1
        return order
    return get_order


def get_player_dict(players: list[Player]) -> dict[int, Player]:
    return {player.player_id: player for player in players}


@pytest.fixture
def coal_market():
    def get_coal_market(players: dict[int, Player] = {}) -> ResourceMarket:
        return ResourceMarket(Resource.coal, players)
    return get_coal_market


@pytest.fixture
def energy_market():
    return EnergyMarket()


@pytest.fixture
def get_power_plant():
    plant_id = 0

    def get_power_plant(player_id: int, type: PowerPlantType, powered_on: int = True, **kwargs):
        nonlocal plant_id
        power_plant = PowerPlant(
            power_plant_id=plant_id,
            player_id=player_id,
            type=type,
            price=100,
            powered_on=powered_on,
            **kwargs
        )
        plant_id += 1
        return power_plant
    return get_power_plant
