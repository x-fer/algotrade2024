from datetime import datetime, timedelta
import pytest
import random
from model import Order, OrderSide, Trade, Resource


@pytest.fixture(autouse=True)
def random_seed():
    random.seed(42)


@pytest.fixture
def traders():
    return [
        {
            'id': x,
            'money': 100000,
            'stocks': 1000
        }
        for x in range(1000)
    ]


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
def get_random_order(get_order_id, get_order, traders):
    def get_random_order():
        player_id = random.choice(traders)['id']
        order_side = random.choice([OrderSide.BUY, OrderSide.SELL])
        price = random.randint(500, 1500)
        size = random.randint(100, 1000)
        return get_order(player_id, price, size, order_side)
    return get_random_order


@pytest.fixture()
def get_order(get_timestamp, get_order_id):
    def get_order(player_id: int, price: int, size: int, order_side: OrderSide, time=0, expiration=2, tick=1):
        return Order(timestamp=get_timestamp(time),
                     expiration_tick=expiration,
                     order_id=get_order_id(),
                     player_id=player_id,
                     game_id=1,
                     price=price,
                     size=size,
                     order_side=order_side,
                     tick=tick,
                     resource=Resource.coal)
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
            assert trade.filled_money == 0  # pragma: no cover
            assert trade.filled_size == 0  # pragma: no cover
            assert trade.filled_price is None  # pragma: no cover
            return {"can_buy": False, "can_sell": False}  # pragma: no cover

        buyer_id = buy_order.player_id
        seller_id = sell_order.player_id

        can_buy = traders[buyer_id]['money'] >= trade.filled_money
        can_sell = traders[seller_id]['stocks'] >= trade.filled_size

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}

        traders[buyer_id]['money'] -= trade.filled_money
        traders[buyer_id]['stocks'] += trade.filled_size

        traders[seller_id]['money'] += trade.filled_money
        traders[seller_id]['stocks'] -= trade.filled_size

        return {"can_buy": True, "can_sell": True}
    return check_trade
