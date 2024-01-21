import pytest
from config import config
from collections import deque
import pandas as pd
from xheap import XHeap
import random
from . import Trade, Order, OrderBook, OrderType, OrderSide, TradeStatus


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


@pytest.fixture
def get_order_id():
    order_id = 0

    def get_order_id():
        nonlocal order_id
        order_id += 1
        return order_id
    return get_order_id


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
                        TradeStatus.PENDING)

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


def test_zero_sum(traders, on_add_true, check_trade, get_random_order):
    # random.seed(42)
    on_add = on_add_true

    money_sum = sum([x['money'] for x in traders])
    stocks_sum = sum([x['stocks'] for x in traders])

    orderbook = OrderBook()
    orderbook.register_callback('check_add', on_add)
    orderbook.register_callback('check_trade', check_trade)

    l = []
    for _ in range(500):
        # t1 = pd.Timestamp.now()
        for _ in range(100):
            order = get_random_order()
            if order is None:
                continue
            orderbook.add_order(order)
        # print(ob.match(pd.Timestamp.now()))

        if len(orderbook.buy_side) == 0 or len(orderbook.sell_side) == 0:
            continue
        buy_side = orderbook.buy_side.peek().price
        sell_side = orderbook.sell_side.peek().price

        l.append((buy_side, sell_side))
        # t1 = (pd.Timestamp.now() - t1).total_seconds()
        # print(t1)
    orderbook.cancel_all()

    # plt.plot([x[0] for x in l])
    # plt.plot([x[1] for x in l])
    # plt.show()

    money_sum_after = sum([x['money'] for x in traders])
    stocks_sum_after = sum([x['stocks'] for x in traders])

    # print(money_sum, money_sum_after)
    # print(stocks_sum, stocks_sum_after)

    # pprint(traders)

    # plot money distribution
    # plt.hist([x['money'] for x in traders], bins=100)
    # plt.show()

    # # plot stocks distribution
    # plt.hist([x['stocks'] for x in traders], bins=100)
    # plt.show()

    assert money_sum == money_sum_after
    assert stocks_sum == stocks_sum_after

