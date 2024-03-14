from copy import deepcopy
import pytest
from fixtures.fixtures import *
from model.order_types import OrderSide, OrderStatus


@pytest.fixture
def get_markets():
    def get_markets(player_dict):
        markets = {
            x.value: ResourceMarket(x)
            for x in Resource
        }
        for market in markets.values():
            market.set_players(player_dict)
        return markets
    return get_markets


def test_run_markets_no_match(get_tick_data, get_order, ticker, get_player, coal_market, get_markets):
    order1 = get_order(player_id=1, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)
    order2 = get_order(player_id=2, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)

    fresh_order1 = deepcopy(order1)
    fresh_order2 = deepcopy(order2)

    player1 = get_player(money=100, coal=0)
    player2 = get_player(money=0, coal=100)

    player_dict = get_player_dict([player1, player2])

    markets = get_markets(player_dict)

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[
            order1, order2
        ],
        updated_orders={},
        players=player_dict,
        markets=markets
    )

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id] == fresh_order1
    assert tick_data.updated_orders[order2.order_id] == fresh_order2
    assert len(tick_data.updated_orders) == 2


def test_run_markets_match(get_tick_data, get_order, ticker, get_player, coal_market, get_markets):
    order1 = get_order(player_id=1, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)
    order2 = get_order(player_id=2, price=5, size=25,
                       order_side=OrderSide.SELL, tick=1)

    player1 = get_player(money=1000, coal=0)
    player2 = get_player(money=0, coal=100)

    player_dict = get_player_dict([player1, player2])

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[
            order1, order2
        ],
        updated_orders={},
        players=player_dict,
        markets=get_markets(player_dict),
    )

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id].order_status == OrderStatus.ACTIVE
    assert tick_data.updated_orders[order2.order_id].order_status == OrderStatus.COMPLETED

    assert tick_data.updated_orders[order1.order_id].filled_size == 25
    assert tick_data.updated_orders[order1.order_id].filled_money == 125
    assert tick_data.updated_orders[order1.order_id].filled_price == 5

    assert tick_data.updated_orders[order2.order_id].filled_size == 25
    assert tick_data.updated_orders[order2.order_id].filled_money == 125
    assert tick_data.updated_orders[order2.order_id].filled_price == 5

    assert len(tick_data.updated_orders) == 2


def test_run_markets_match_insufficient_funds(get_tick_data, get_order, ticker, get_player, coal_market, get_markets):

    order1 = get_order(player_id=1, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)
    order2 = get_order(player_id=2, price=5, size=25,
                       order_side=OrderSide.SELL, tick=1)

    player1 = get_player(money=124, coal=0)  # needs 125
    player2 = get_player(money=0, coal=100)

    player_dict = get_player_dict([player1, player2])

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[
            order1, order2
        ],
        updated_orders={},
        players=player_dict,
        markets=get_markets(player_dict)
    )

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id].order_status == OrderStatus.CANCELLED
    assert tick_data.updated_orders[order2.order_id].order_status == OrderStatus.ACTIVE

    assert tick_data.updated_orders[order1.order_id].filled_size == 0
    assert tick_data.updated_orders[order1.order_id].filled_money == 0
    assert tick_data.updated_orders[order1.order_id].filled_price == 0

    assert tick_data.updated_orders[order2.order_id].filled_size == 0
    assert tick_data.updated_orders[order2.order_id].filled_money == 0
    assert tick_data.updated_orders[order2.order_id].filled_price == 0

    assert len(tick_data.updated_orders) == 2


def test_run_markets_match_insufficient_resources(get_tick_data, get_order, ticker, get_player, coal_market, get_markets):

    order1 = get_order(player_id=1, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)
    order2 = get_order(player_id=2, price=5, size=25,
                       order_side=OrderSide.SELL, tick=1)

    player1 = get_player(money=1000, coal=0)
    player2 = get_player(money=0, coal=24)  # needs 25

    player_dict = get_player_dict([player1, player2])

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[
            order1, order2
        ],
        updated_orders={},
        players=player_dict,

        markets=get_markets(player_dict)
    )

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id].order_status == OrderStatus.ACTIVE
    assert tick_data.updated_orders[order2.order_id].order_status == OrderStatus.CANCELLED

    assert tick_data.updated_orders[order1.order_id].filled_size == 0
    assert tick_data.updated_orders[order1.order_id].filled_money == 0
    assert tick_data.updated_orders[order1.order_id].filled_price == 0

    assert tick_data.updated_orders[order2.order_id].filled_size == 0
    assert tick_data.updated_orders[order2.order_id].filled_money == 0
    assert tick_data.updated_orders[order2.order_id].filled_price == 0

    assert len(tick_data.updated_orders) == 2


def test_run_markets_cancel(get_tick_data, get_order, ticker, get_player, coal_market, get_markets):
    order1 = get_order(player_id=1, price=5, size=50,
                       order_side=OrderSide.BUY, tick=1)
    order1_cancelled = deepcopy(order1)
    order1_cancelled.order_status = OrderStatus.CANCELLED
    order2 = get_order(player_id=2, price=5, size=25,
                       order_side=OrderSide.SELL, tick=1)

    player1 = get_player(money=1000, coal=0)
    player2 = get_player(money=0, coal=100)

    player_dict = get_player_dict([player1, player2])

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[],
        updated_orders={},
        players=player_dict,
        markets=get_markets(player_dict)
    )

    tick_data.pending_orders = [order1]

    tick_data.game.current_tick = 1
    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id].order_status == OrderStatus.ACTIVE
    assert len(tick_data.updated_orders) == 1

    tick_data.game.current_tick = 2
    tick_data.pending_orders = []
    tick_data.updated_orders = {}
    tick_data.user_cancelled_orders = [order1_cancelled]

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order1.order_id].order_status == OrderStatus.CANCELLED
    assert len(tick_data.updated_orders) == 1

    tick_data.game.current_tick = 3
    tick_data.pending_orders = [order2]
    tick_data.updated_orders = {}
    tick_data.user_cancelled_orders = []

    tick_data = ticker.run_markets(tick_data)

    assert tick_data.updated_orders[order2.order_id].order_status == OrderStatus.ACTIVE
    assert len(tick_data.updated_orders) == 1
    assert tick_data.updated_orders[order2.order_id].filled_size == 0
    assert tick_data.updated_orders[order2.order_id].filled_money == 0
    assert tick_data.updated_orders[order2.order_id].filled_price == 0
