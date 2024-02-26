from .price_tracker import PriceTracker
from game.orderbook import OrderBook
from game.fixtures.orderbook_fixtures import *
from model import OrderSide


def test_price_tracker(get_order, get_timestamp):
    orderbook = OrderBook()
    price_tracker = PriceTracker(orderbook)
    orderbook.add_order(get_order(player_id=1, price=5,
                        size=50, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=2, price=5,
                        size=50, order_side=OrderSide.SELL))
    orderbook.add_order(get_order(player_id=3, price=10,
                        size=50, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=4, price=10,
                        size=50, order_side=OrderSide.SELL))
    orderbook.add_order(get_order(player_id=5, price=15,
                        size=50, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=6, price=15,
                        size=50, order_side=OrderSide.SELL))
    orderbook.add_order(get_order(player_id=7, price=3,
                        size=50, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=8, price=3,
                        size=50, order_side=OrderSide.SELL))

    orderbook.match(timestamp=get_timestamp(1))

    assert price_tracker.get_high() == 15
    assert price_tracker.get_low() == 3
    assert price_tracker.get_average() == 8.25
    assert price_tracker.get_open() == 5
    assert price_tracker.get_close() == 3

    orderbook.add_order(get_order(player_id=5, price=30,
                        size=50, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=6, price=30,
                        size=50, order_side=OrderSide.SELL))

    orderbook.match(timestamp=get_timestamp(1))

    assert price_tracker.get_high() == 30
    assert price_tracker.get_low() == 30
    assert price_tracker.get_average() == 30
    assert price_tracker.get_open() == 30
    assert price_tracker.get_close() == 30


def test_price_tracker_market_weighted(get_order, get_timestamp):
    orderbook = OrderBook()
    price_tracker = PriceTracker(orderbook)
    orderbook.add_order(get_order(player_id=3, price=5,
                        size=1, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=4, price=5,
                        size=1, order_side=OrderSide.SELL))
    orderbook.add_order(get_order(player_id=5, price=25,
                        size=3, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=6, price=25,
                        size=3, order_side=OrderSide.SELL))

    orderbook.match(timestamp=get_timestamp(1))

    assert price_tracker.get_high() == 25
    assert price_tracker.get_low() == 5
    assert price_tracker.get_average() == 20


def test_price_tracker_market_no_trades(get_order, get_timestamp):
    orderbook = OrderBook()
    price_tracker = PriceTracker(orderbook)
    orderbook.add_order(get_order(player_id=3, price=5,
                        size=1, order_side=OrderSide.BUY))
    orderbook.add_order(get_order(player_id=4, price=5,
                        size=1, order_side=OrderSide.SELL))

    orderbook.match(timestamp=get_timestamp(1))

    assert len(orderbook.match_trades) == 1
    assert price_tracker.get_average() == 5
    orderbook.match(timestamp=get_timestamp(1))
    assert len(orderbook.match_trades) == 0
    assert price_tracker.get_average() == 5
