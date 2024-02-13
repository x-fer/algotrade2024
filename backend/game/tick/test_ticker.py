
# def run_markets(self, tick_data: TickData, tick: int):
#         updated_orders = {}
#         for order in tick_data.user_cancelled_orders:
#             game_data = self.game_data[tick_data.game.game_id]
#             market = game_data.markets[order.resource.value]
#             updated = market.cancel(order)
#             updated_orders.update(updated)
#         for order in tick_data.pending_orders:
#             game_data = self.game_data[tick_data.game.game_id]
#             market = game_data.markets[order.resource.value]
#             updated = market.match(order, tick)
#             updated_orders.update(updated)
#         tick_data.updated_orders.extend(updated_orders)
#         return tick_data

import pytest
from game.tick import TickData
from game.fixtures.fixtures import *
from model.order_types import OrderSide, OrderStatus
from model.player import Player

# test


def test_run_markets(get_tick_data, get_order, get_ticker, get_player, get_power_plant):
    ticker = get_ticker()

    tick_data = get_tick_data(
        user_cancelled_orders=[],
        pending_orders=[
            get_order(player_id=1, price=5, size=50,
                      order_side=OrderSide.BUY, tick=1),
            get_order(player_id=2, price=5, size=50,
                      order_side=OrderSide.BUY, tick=1)

        ],
        updated_orders=[],
        players={
            1: get_player(money=100, coal=0),
            2: get_player(money=0, coal=100)
        },
        power_plants={},
        markets={}
    )

    # TODO
