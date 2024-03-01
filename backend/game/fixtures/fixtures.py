from typing import Dict, List
import pandas as pd
from game.tick import TickData, Ticker
from game.tick.ticker import GameData
from model import Order, Player, Resource, Game, PowerPlantType, OrderSide
from game.market import ResourceMarket, EnergyMarket
import pytest
from model.dataset_data import DatasetData

from model.order_types import OrderStatus


@pytest.fixture
def game_id():
    return 1


@pytest.fixture
def dataset_row():
    return DatasetData(
        coal=1,
        uranium=2,
        biomass=3,
        gas=4,
        oil=5,
        geothermal=6,
        wind=7,
        solar=8,
        hydro=9,
        energy_demand=100,
        max_energy_price=1000,
        coal_price=1,
        uranium_price=2,
        biomass_price=3,
        gas_price=4,
        oil_price=5,
    )


@pytest.fixture
def game():
    return Game(game_id=1,
                game_name=f"game_{game_id}",
                is_contest=False,
                bots="",
                dataset_id=1,
                start_time=pd.Timestamp.now(),
                total_ticks=1000,
                tick_time=1000,
                )


@pytest.fixture
def team_id():
    return 1


@pytest.fixture
def get_game_data(game):
    game_id = 1

    def get_game_data(**kwargs) -> Game:
        nonlocal game_id
        game_data = GameData(game, **kwargs)
        return game_data

    return get_game_data


@pytest.fixture
def get_ticker(game, get_game_data):
    def get_ticker(players) -> Ticker:
        ticker = Ticker()
        ticker.game_data = {1: get_game_data(players=players)}
        return ticker
    return get_ticker


@pytest.fixture
def get_tick_data(game_id):
    def get_tick_data(markets, players, user_cancelled_orders=[], pending_orders=[], updated_orders=[], coal=100, energy_demand=100, max_energy_price=100) -> TickData:
        tick_data = TickData(
            game=Game(
                game_id=game_id,
                game_name=f"game_{game_id}",
                is_contest=False,
                bots="",
                dataset_id=1,
                start_time=pd.Timestamp.now(),
                total_ticks=1000,
                tick_time=1000,
            ),
            bots=[],
            dataset_row=DatasetData(
                dataset_data_id=1,
                dataset_id=1,
                date=pd.Timestamp.now(),
                tick=1,
                coal=coal,
                uranium=2,
                biomass=3,
                gas=4,
                oil=5,
                coal_price=coal,
                uranium_price=2,
                biomass_price=3,
                gas_price=4,
                oil_price=5,
                geothermal=6,
                wind=7,
                solar=8,
                hydro=9,
                energy_demand=energy_demand,
                max_energy_price=max_energy_price
            ),
            markets=markets,
            players=players,
            user_cancelled_orders=user_cancelled_orders,
            pending_orders=pending_orders,
            updated_orders=updated_orders
        )

        return tick_data
    return get_tick_data


@pytest.fixture
def get_player(game_id, team_id):
    player_id = 1

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
def get_player_in_game(team_id):
    player_id = 1

    def get_player_in_game(**kwargs) -> Player:
        nonlocal player_id
        player = Player(
            player_id=player_id,
            player_name=f"player_{player_id}",
            team_id=team_id,
            **kwargs
        )
        player_id += 1
        return player

    return get_player_in_game


@pytest.fixture
def get_order():
    order_id = 0

    def get_order(player_id: int, price: int, size: int, order_side: OrderSide, tick: int) -> Order:
        nonlocal order_id
        order = Order(
            order_id=order_id,
            game_id=1,
            timestamp=pd.Timestamp.now(),
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


def get_player_dict(players: List[Player]) -> Dict[int, Player]:
    return {player.player_id: player for player in players}


@pytest.fixture
def coal_market():
    def get_coal_market(players: Dict[int, Player] = {}) -> ResourceMarket:
        return ResourceMarket(Resource.coal, players)
    return get_coal_market


@pytest.fixture
def energy_market():
    return EnergyMarket()


@pytest.fixture
def get_energy_market():
    def get_energy_market() -> EnergyMarket:
        return EnergyMarket()
    return get_energy_market
