import pytest
import pandas as pd
import random
from orderbook import Trade, Order, OrderType, OrderSide, OrderStatus


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
def get_order_id():
    order_id = 0

    def get_order_id():
        nonlocal order_id
        order_id += 1
        return order_id
    return get_order_id


@pytest.fixture(autouse=True)
def get_timestamp():
    tm = pd.Timestamp.now()

    def get_timestamp(time: int):
        nonlocal tm
        return tm + pd.Timedelta(seconds=time)
    return get_timestamp


@pytest.fixture
def get_random_order(get_order_id, traders):
    def get_random_order():
        random_trader = random.choice(traders)

        buy_sell = random.choice([OrderSide.BUY, OrderSide.SELL])
        type = random.choice([OrderType.LIMIT])

        price = random.randint(500, 1500)
        size = random.randint(100, 1000)

        tm = pd.Timestamp.now()

        order = Order(tm, tm + pd.Timedelta(seconds=1),
                      get_order_id(), random_trader['id'],
                      price, size, 0, 0,
                      buy_sell, type,
                      OrderStatus.PENDING)

        return order
    return get_random_order


@pytest.fixture
def check_trade(traders):
    def check_trade(trade: Trade):
        buy_order = trade.buy_order
        sell_order = trade.sell_order

        if buy_order is None or sell_order is None:
            assert trade.filled_money == 0
            assert trade.filled_size == 0
            assert trade.filled_price is None
            return {"can_buy": False, "can_sell": False}

        buyer_id = buy_order.trader_id
        seller_id = sell_order.trader_id

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


@pytest.fixture()
def get_order(get_timestamp, get_order_id):
    def get_order(trader_id: int, price: int, size: int, order_side: OrderSide, time=0, expiration=2):
        return Order(get_timestamp(time), get_timestamp(expiration), get_order_id(), trader_id,
                     price, size, 0, 0, order_side, OrderType.LIMIT, OrderStatus.PENDING)
    return get_order
