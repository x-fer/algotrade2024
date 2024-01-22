from config import config
from unittest.mock import Mock
from . import Trade, OrderBook, OrderSide, OrderStatus
from .fixtures import *

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

