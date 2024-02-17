from datetime import datetime
import pytest
from game.tick.ticker import TickData, Ticker, GameData
from model import Game, Player, PowerPlant, Order, OrderStatus, Resource


@pytest.fixture
def sample_game():
    return Game(
        game_id=1,
        game_name="Sample Game",
        start_time=datetime(2024, 1, 1),
        current_tick=1,
        total_ticks=10,
        is_finished=False,
        dataset_id=1,
        bots="",
        tick_time=1000,
        is_contest=False
    )


@pytest.fixture
def sample_players():
    return {
        1: Player(player_id=1, game_id=1, player_name="Player 1", energy=0, team_id=1),
        2: Player(player_id=2, game_id=1, player_name="Player 2", energy=0, team_id=1)
    }


@pytest.fixture
def ticker(sample_game, sample_players):
    t = Ticker()
    t.game_data[sample_game.game_id] = GameData(sample_game, sample_players)

    return t


@pytest.fixture
def sample_power_plants():
    return {
        1: [
            PowerPlant(power_plant_id=1, player_id=1, type=1, price=100,
                       temperature=0.5, powered_on=True),
            PowerPlant(power_plant_id=2, player_id=1, type=2, price=100,
                       temperature=0.6, powered_on=True)
        ],
        2: [
            PowerPlant(power_plant_id=3, player_id=2, type=1, price=100,
                       temperature=0.7, powered_on=True)
        ]
    }


@pytest.fixture
def sample_pending_orders():
    return [
        Order(order_id=1, game_id=1, player_id=1, order_type="BUY", order_side="SELL",
              order_status=OrderStatus.PENDING, resource=Resource.coal, price=50, size=100, tick=1, timestamp=datetime.now()),
        Order(order_id=2, game_id=1, player_id=2, order_type="BUY",
              order_side="SELL", order_status=OrderStatus.PENDING, resource=Resource.oil, price=50, size=100, tick=1, timestamp=datetime.now())
    ]


@pytest.fixture
def sample_user_cancelled_orders():
    return [
        Order(order_id=3, game_id=1, player_id=1, order_type="BUY", order_side="SELL",
              order_status=OrderStatus.USER_CANCELLED, resource=Resource.coal, price=50, size=100, tick=1, timestamp=datetime.now()),
        Order(order_id=4, game_id=1, player_id=2, order_type="BUY", order_side="SELL",
              order_status=OrderStatus.USER_CANCELLED, resource=Resource.oil, price=50, size=100, tick=1, timestamp=datetime.now())
    ]


@pytest.fixture
def sample_dataset_row():
    return {"energy_demand": 100, "max_energy_price": 50}


@pytest.fixture
def tick_data(sample_game, sample_players):
    return TickData(
        game=sample_game,
        players=sample_players,
        power_plants={},
        markets={},
        bots=[],
        dataset_row={},
        pending_orders=[],
        user_cancelled_orders=[],
        updated_orders={}
    )
