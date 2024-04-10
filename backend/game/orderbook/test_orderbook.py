from typing import Dict, List
from unittest.mock import Mock
from .orderbook import OrderBook
from model import OrderSide, OrderStatus, Trade, Player
from fixtures.orderbook_fixtures import *


class TestCancelTrade():
    def test_after_match(self, get_order):
        sample_mock = Mock()
        orderbook = OrderBook()
        orderbook.register_callback('on_cancel', sample_mock.some_method)
        buy_order = get_order(player_id=1, price=5,
                              size=50, order_side=OrderSide.BUY, tick=1)

        orderbook.add_order(buy_order)
        orderbook.match(tick=1)

        assert len(orderbook.buy_side) == 1
        assert buy_order.order_status == OrderStatus.ACTIVE
        orderbook.cancel_order(buy_order.order_id)
        assert len(orderbook.buy_side) == 0
        sample_mock.some_method.assert_called_with(buy_order)
        assert buy_order.order_status == OrderStatus.CANCELLED

    def test_expire(self, get_order):
        sample_mock = Mock()
        orderbook = OrderBook()
        orderbook.register_callback('on_cancel', sample_mock.some_method)
        buy_order = get_order(player_id=1, price=5, size=50,
                              order_side=OrderSide.BUY, expiration=4, tick=1)

        orderbook.add_order(buy_order)
        orderbook.match(tick=1)

        sample_mock.some_method.assert_not_called()
        assert len(orderbook.buy_side) == 1
        assert buy_order.order_status == OrderStatus.ACTIVE
        orderbook.match(tick=5)
        assert len(orderbook.buy_side) == 0
        sample_mock.some_method.assert_called_with(buy_order)
        assert buy_order.order_status == OrderStatus.EXPIRED


class TestCheckTrade():
    def test_when_both_true(self, get_order):
        def check_trade(*args, **kwargs):
            return {'can_buy': True, 'can_sell': True}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        price = 5
        size = 50
        buy_order = get_order(player_id=1, price=price,
                              size=size, order_side=OrderSide.BUY, tick=1)
        sell_order = get_order(player_id=2, price=price,
                               size=size, order_side=OrderSide.SELL, tick=1)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)

        orderbook.match(tick=1)

        assert len(orderbook.match_trades) == 1
        trade: Trade = orderbook.match_trades[0]
        assert trade.buy_order is buy_order
        assert trade.sell_order is sell_order
        assert trade.buy_order.order_status == OrderStatus.COMPLETED
        assert trade.sell_order.order_status == OrderStatus.COMPLETED
        assert trade.total_money == price * size
        assert trade.trade_price == price
        assert trade.trade_size == size
        assert trade.tick == 1

    def test_when_both_false(self, get_order):
        def check_trade(*args, **kwargs):
            return {'can_buy': False, 'can_sell': False}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        buy_order = get_order(player_id=1, price=5,
                              size=50, order_side=OrderSide.BUY, tick=1)
        sell_order = get_order(player_id=2, price=5,
                               size=50, order_side=OrderSide.SELL, tick=1)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)

        orderbook.match(tick=1)

        assert len(orderbook.match_trades) == 0
        assert len(orderbook.buy_side) == 0
        assert len(orderbook.sell_side) == 0
        assert buy_order.order_status == OrderStatus.CANCELLED
        assert sell_order.order_status == OrderStatus.CANCELLED
        assert buy_order.filled_money == 0
        assert buy_order.filled_size == 0
        assert sell_order.filled_money == 0
        assert sell_order.filled_size == 0

    def test_when_one_false(self, get_order):        
        def check_trade(*args, **kwargs):
            return {'can_buy': True, 'can_sell': False}

        orderbook = OrderBook()
        orderbook.register_callback('check_trade', check_trade)

        buy_order = get_order(player_id=1, price=5,
                              size=50, order_side=OrderSide.BUY, tick=1)
        sell_order = get_order(player_id=2, price=5,
                               size=50, order_side=OrderSide.SELL, tick=1)
        orderbook.add_order(buy_order)
        orderbook.add_order(sell_order)

        orderbook.match(tick=1)

        assert len(orderbook.match_trades) == 0
        assert len(orderbook.buy_side) == 1
        assert len(orderbook.sell_side) == 0
        assert buy_order.order_status == OrderStatus.ACTIVE
        assert sell_order.order_status == OrderStatus.CANCELLED
        assert buy_order.filled_money == 0
        assert buy_order.filled_size == 0
        assert sell_order.filled_money == 0
        assert sell_order.filled_size == 0

    def test_no_check_trade_same_player_id(self, get_order):
        orderbook = OrderBook()

        orderbook.add_order(get_order(player_id=1, price=5,
                            size=50, order_side=OrderSide.BUY, tick=1))
        orderbook.add_order(get_order(player_id=2, price=5,
                            size=50, order_side=OrderSide.SELL, tick=1))

        orderbook.match(tick=1)

        assert len(orderbook.match_trades) == 1


def test_zero_sum(traders, traders_list, on_add_true, check_trade, get_random_order):
    on_add = on_add_true

    traders: Dict[str, Player]

    money_sum = sum([x.money for x in traders_list])
    stocks_sum = sum([x.resources.coal for x in traders_list])

    orderbook = OrderBook()
    orderbook.register_callback('check_add', on_add)
    orderbook.register_callback('check_trade', check_trade)

    for _ in range(500):
        for _ in range(100):
            order = get_random_order()
            orderbook.add_order(order)
        orderbook.match(order.tick)
    orderbook.cancel_all()

    money_sum_after = sum([x.money for x in traders_list])
    stocks_sum_after = sum([x.resources.coal for x in traders_list])

    assert money_sum == money_sum_after
    assert stocks_sum == stocks_sum_after


def test_add_order_already_exists(get_order):
    orderbook = OrderBook()
    order = get_order(player_id=1, price=5, size=50,
                      order_side=OrderSide.BUY, tick=1)
    orderbook.add_order(order)
    try:
        orderbook.add_order(order)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(e) == f"Order with id {order.order_id} already in queue"


def test_expiration_tick_less_than_tick(get_order):
    orderbook = OrderBook()
    order = get_order(player_id=1, price=5, size=50,
                      order_side=OrderSide.BUY, tick=1, expiration=0)
    try:
        orderbook.add_order(order)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(
            e) == f"Order with id {order.order_id} has expiration earlier than timestamp"


def test_size_less_than_zero(get_order):
    orderbook = OrderBook()
    order = get_order(player_id=1, price=5, size=0,
                      order_side=OrderSide.BUY, tick=1)
    try:
        orderbook.add_order(order)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(e) == f"Order with id {order.order_id} has size <= 0"


def test_rejected(get_order):
    def on_add(*args, **kwargs):
        return False
    orderbook = OrderBook()
    orderbook.register_callback('check_add', on_add)
    order = get_order(player_id=1, price=5, size=50,
                      order_side=OrderSide.BUY, tick=1)
    orderbook.add_order(order)
    assert order.order_status == OrderStatus.REJECTED


def test_cancel_order_not_found():
    orderbook = OrderBook()
    try:
        orderbook.cancel_order(1)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(e) == "Order with id 1 not found"


def test_second_order_is_market_order(get_order):
    orderbook = OrderBook()
    first_order = get_order(player_id=1, price=5, size=50,
                            order_side=OrderSide.BUY, tick=1)
    second_order = get_order(player_id=2, price=5, size=50,
                             order_side=OrderSide.SELL, tick=1)

    trades = []
    orderbook.register_callback('on_trade', lambda trade: trades.append(trade))

    orderbook.add_order(first_order)
    orderbook.add_order(second_order)

    orderbook.match(tick=1)

    assert len(trades) == 1


def test_prev_price(get_order):
    orderbook = OrderBook()
    first_order = get_order(player_id=1, price=5, size=50,
                            order_side=OrderSide.BUY, tick=1)
    second_order = get_order(player_id=2, price=5, size=50,
                             order_side=OrderSide.SELL, tick=1)

    trades: List[Trade] = []
    orderbook.register_callback('on_trade', lambda trade: trades.append(trade))
    orderbook.prev_price = 10

    orderbook.add_order(first_order)
    orderbook.add_order(second_order)

    orderbook.match(tick=1)

    assert len(trades) == 1
    assert trades[0].total_money == 5 * 50


def test_invalid_callback_type():
    orderbook = OrderBook()
    try:
        orderbook.register_callback('invalid', lambda *kwargs: True)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(e) == "Invalid callback type"

    orderbook = OrderBook()
    try:
        orderbook.register_callback('on_trade', 42)
        assert False  # pragma: no cover
    except ValueError as e:
        assert str(e) == "Callback is not callable"
