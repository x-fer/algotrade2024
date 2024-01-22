import pytest
from config import config
import pandas as pd
from unittest.mock import Mock
import random
from . import Trade, Order, OrderBook, OrderType, OrderSide, OrderStatus


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


@pytest.fixture(autouse=True)
def get_order(get_timestamp, get_order_id):
    def get_order(trader_id: int, price: int, size: int, order_side: OrderSide, time=0, expiration=2):
        return Order(get_timestamp(time), get_timestamp(expiration), get_order_id(), trader_id, 
                     price, size, 0, 0, order_side, OrderType.LIMIT, OrderStatus.PENDING)
    return get_order

class TestCancelTrade():
    def test_after_match(self, get_order, get_timestamp):
        sample_mock = Mock()
        orderbook = OrderBook()
        orderbook.register_callback('on_cancel', sample_mock.some_method)
        buy_order = get_order(trader_id=1, price=5, size=50, order_side=OrderSide.BUY)

        orderbook.add_order(buy_order)
        orderbook.match(timestamp=get_timestamp(1))

        assert len(orderbook.buy_side) == 1
        assert buy_order.status == OrderStatus.ACTIVE
        orderbook.cancel_order(buy_order.order_id)
        assert len(orderbook.buy_side) == 0
        sample_mock.some_method.assert_called_with(buy_order)
        assert buy_order.status == OrderStatus.CANCELLED

    def test_expire(self, get_order, get_timestamp):
        sample_mock = Mock()
        orderbook = OrderBook()
        orderbook.register_callback('on_cancel', sample_mock.some_method)
        buy_order = get_order(trader_id=1, price=5, size=50, order_side=OrderSide.BUY, expiration=2)

        orderbook.add_order(buy_order)
        orderbook.match(timestamp=get_timestamp(1))
        
        sample_mock.some_method.assert_not_called()
        assert len(orderbook.buy_side) == 1
        assert buy_order.status == OrderStatus.ACTIVE
        orderbook.match(timestamp=get_timestamp(5))
        assert len(orderbook.buy_side) == 0
        sample_mock.some_method.assert_called_with(buy_order)
        assert buy_order.status == OrderStatus.EXPIRED

class TestCheckTrade():
    def test_when_both_true(self, get_order, get_timestamp):
        check_trade = lambda *kwargs: {'can_buy': True, 'can_sell': True}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        price = 5
        size = 50
        buy_order = get_order(trader_id=1, price=price, size=size, order_side=OrderSide.BUY)
        sell_order = get_order(trader_id=2, price=price, size=size, order_side=OrderSide.SELL)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)
        
        orderbook.match(timestamp=get_timestamp(1))

        assert len(orderbook.match_trades) == 1
        trade: Trade = orderbook.match_trades[0]
        assert trade.buy_order == buy_order
        assert trade.sell_order == sell_order
        assert trade.buy_order.status == OrderStatus.COMPLETED
        assert trade.sell_order.status == OrderStatus.COMPLETED
        assert trade.filled_money == price * size
        assert trade.filled_size == size
        assert trade.timestamp == get_timestamp(1)
    
    def test_when_both_false(self, get_order, get_timestamp):
        check_trade = lambda *kwargs: {'can_buy': False, 'can_sell': False}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        buy_order = get_order(trader_id=1, price=5, size=50, order_side=OrderSide.BUY)
        sell_order = get_order(trader_id=2, price=5, size=50, order_side=OrderSide.SELL)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)
        
        orderbook.match(timestamp=get_timestamp(1))

        assert len(orderbook.match_trades) == 0
        assert len(orderbook.buy_side) == 0
        assert len(orderbook.sell_side) == 0
        assert buy_order.status == OrderStatus.CANCELLED
        assert sell_order.status == OrderStatus.CANCELLED
        assert buy_order.filled_money == 0
        assert buy_order.filled_size == 0
        assert sell_order.filled_money == 0
        assert sell_order.filled_size == 0
    
    def test_when_one_false(self, get_order, get_timestamp):
        check_trade = lambda *kwargs: {'can_buy': True, 'can_sell': False}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        buy_order = get_order(trader_id=1, price=5, size=50, order_side=OrderSide.BUY)
        sell_order = get_order(trader_id=2, price=5, size=50, order_side=OrderSide.SELL)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)
        
        orderbook.match(timestamp=get_timestamp(1))

        assert len(orderbook.match_trades) == 0
        assert len(orderbook.buy_side) == 1
        assert len(orderbook.sell_side) == 0
        assert buy_order.status == OrderStatus.ACTIVE
        assert sell_order.status == OrderStatus.CANCELLED
        assert buy_order.filled_money == 0
        assert buy_order.filled_size == 0
        assert sell_order.filled_money == 0
        assert sell_order.filled_size == 0

    def test_no_check_trade_same_trader_id(self, get_order, get_timestamp):
        orderbook = OrderBook()

        orderbook.add_order(get_order(trader_id=1, price=5, size=50, order_side=OrderSide.BUY))
        orderbook.add_order(get_order(trader_id=2, price=5, size=50, order_side=OrderSide.SELL))

        orderbook.match(timestamp=get_timestamp(1))

        assert len(orderbook.match_trades) == 1


def test_zero_sum(traders, on_add_true, check_trade, get_random_order):
    on_add = on_add_true

    money_sum = sum([x['money'] for x in traders])
    stocks_sum = sum([x['stocks'] for x in traders])

    orderbook = OrderBook()
    orderbook.register_callback('check_add', on_add)
    orderbook.register_callback('check_trade', check_trade)

    for _ in range(500):
        for _ in range(100):
            order = get_random_order()
            if order is None:
                continue
            orderbook.add_order(order)
        orderbook.match(order.timestamp)
    orderbook.cancel_all()

    money_sum_after = sum([x['money'] for x in traders])
    stocks_sum_after = sum([x['stocks'] for x in traders])

    assert money_sum == money_sum_after
    assert stocks_sum == stocks_sum_after

