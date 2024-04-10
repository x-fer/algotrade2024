from datetime import datetime
import pytest
from game.market import EnergyMarket
from game.tick import TickData, Ticker, GameData
from model import Game, Player, Order, OrderStatus, Resource
from model.order_types import OrderSide


@pytest.fixture
def sample_game():
    return Game(
        game_id="1",
        game_name="Sample Game",
        start_time=datetime(2024, 1, 1),
        current_tick=1,
        total_ticks=10,
        is_finished=False,
        dataset_id="1",
        bots="",
        tick_time=1000,
        is_contest=False
    )


@pytest.fixture
def sample_game_data(sample_game):
    return GameData(sample_game)


@pytest.fixture
def sample_players():
    return {
        1: Player(player_id="1", game_id="1", player_name="Player 1", energy=0, team_id="1", wind_plants_owned=2, wind_plants_powered=2),
        2: Player(player_id="2", game_id="1", player_name="Player 2", energy=0, team_id="1", coal=100, coal_plants_powered=2, coal_plants_owned=2)
    }


@pytest.fixture
def sample_energy_market():
    return EnergyMarket()


@pytest.fixture
def ticker(sample_game, sample_game_data):
    t = Ticker()
    t.game_data[sample_game.game_id] = sample_game_data
    return t


@pytest.fixture
def sample_pending_orders():
    return [
        Order(order_id="1", game_id="1", player_id="1", order_side=OrderSide.SELL,
              order_status=OrderStatus.PENDING, resource=Resource.COAL, price=50, size=100, tick=1, timestamp=datetime.now()),
        Order(order_id="2", game_id="1", player_id="2", order_side=OrderSide.SELL, 
              order_status=OrderStatus.PENDING, resource=Resource.OIL, price=50, size=100, tick=1, timestamp=datetime.now())
    ]


@pytest.fixture
def sample_user_cancelled_orders():
    return [
        Order(order_id="3", game_id="1", player_id="1", order_side=OrderSide.SELL,
              order_status=OrderStatus.USER_CANCELLED, resource=Resource.COAL, price=50, size=100, tick=1, timestamp=datetime.now()),
        Order(order_id="4", game_id="1", player_id="2", order_side=OrderSide.SELL,
              order_status=OrderStatus.USER_CANCELLED, resource=Resource.OIL, price=50, size=100, tick=1, timestamp=datetime.now())
    ]


@pytest.fixture
def sample_dataset_row():
    return {"energy_demand": 100, "max_energy_price": 50, "coal": 100, "oil": 100, "uranium": 100, 'biomass': 100, 'gas': 100, 'geothermal': 100, 'solar': 100, 'wind': 100, 'hydro': 100}


@pytest.fixture
def tick_data(sample_game, sample_players, sample_energy_market):
    return TickData(
        game=sample_game,
        players=sample_players,
        markets={},
        energy_market=sample_energy_market,
        bots=[],
        dataset_row={},
        pending_orders=[],
        user_cancelled_orders=[],
        updated_orders={}
    )
