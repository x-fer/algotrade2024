from datetime import datetime, timedelta
import pytest
import random
from fixtures.fixtures import get_player_dict
from model import Order, OrderSide, Trade, Resource
from model.player import Player
from model.power_plant_model import ResourcesModel


@pytest.fixture(autouse=True)
def random_seed():
    random.seed(42)


@pytest.fixture
def traders_list():
    return [
        Player(
            pk=str(x),
            player_name=str(x),
            game_id="1",
            team_id="2",
            money=100000,
            resources=ResourcesModel(coal=1000),
        )
        for x in range(1000)
    ]


@pytest.fixture
def traders(traders_list):
    return get_player_dict(traders_list)


@pytest.fixture
def on_add_true(traders):
    def on_insert(order: Order):
        return True

    return on_insert


@pytest.fixture(autouse=True)
def get_timestamp():
    tm = datetime.now()

    def get_timestamp(time: int):
        nonlocal tm
        return tm + timedelta(seconds=time)

    return get_timestamp


@pytest.fixture
def get_random_order(get_order, traders_list):
    def get_random_order():
        player_id = random.choice(traders_list).player_id
        order_side = random.choice([OrderSide.BUY, OrderSide.SELL])
        price = random.randint(500, 1500)
        size = random.randint(100, 1000)
        return get_order(player_id, price, size, order_side)

    return get_random_order


@pytest.fixture()
def get_order(get_timestamp, get_order_id):
    def get_order(
        player_id: str,
        price: int,
        size: int,
        order_side: OrderSide,
        time=0,
        expiration=5,
        tick=1,
    ):
        return Order(
            timestamp=get_timestamp(time),
            expiration_tick=expiration,
            order_id=str(get_order_id()),
            player_id=player_id,
            game_id="1",
            price=price,
            size=size,
            order_side=order_side.value,
            tick=tick,
            resource=Resource.COAL.value,
        )

    return get_order


@pytest.fixture(autouse=True)
def get_order_id():
    order_id = 0

    def get_order_id():
        nonlocal order_id
        order_id += 1
        return order_id

    return get_order_id


@pytest.fixture
def check_trade(traders):
    def check_trade(trade: Trade):
        buy_order = trade.buy_order
        sell_order = trade.sell_order

        if buy_order is None or sell_order is None:
            assert trade.total_price == 0
            assert trade.trade_size == 0
            assert trade.trade_price is None
            return {"can_buy": False, "can_sell": False}

        buyer_id = buy_order.player_id
        seller_id = sell_order.player_id

        can_buy = traders[buyer_id].money >= trade.total_price
        can_sell = traders[seller_id].resources.coal >= trade.trade_size

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}

        traders[buyer_id].money -= trade.total_price
        traders[buyer_id].resources.coal += trade.trade_size

        traders[seller_id].money += trade.total_price
        traders[seller_id].resources.coal -= trade.trade_size

        return {"can_buy": True, "can_sell": True}

    return check_trade
