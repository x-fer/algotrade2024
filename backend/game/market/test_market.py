from db.model.order_types import OrderSide, OrderStatus
from db.model import Order, Player
from . import Market
from ..common.fixtures import *


class TestMoneyUpdate():
    def test_when_transaction_successful(self, get_player, get_order, coal_market: Market):
        player_1: Player = get_player(money=100, coal=0)
        player_2: Player = get_player(money=0, coal=100)
        order_1: Order = get_order(player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY)
        order_2: Order = get_order(player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL)
        order_3: Order = get_order(player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL)
        players = get_player_dict([player_1, player_2])

        coal_market.set_players(players)
        coal_market.orderbook.add_order(order_3)
        coal_market.orderbook.match(1)
        coal_market.set_players(players)
        coal_market.orderbook.add_order(order_1)
        coal_market.orderbook.add_order(order_2)
        coal_market.orderbook.match(1)

        assert player_1.money == 0
        assert player_1.coal == 100
        assert player_2.money == 100
        assert player_2.coal == 0
        assert order_1.order_id in coal_market.updated_orders
        assert order_2.order_id in coal_market.updated_orders
        assert order_3.order_id not in coal_market.updated_orders
        assert coal_market.updated_orders[order_1.order_id] is order_1
        assert coal_market.updated_orders[order_2.order_id] is order_2
        assert order_1.order_status == OrderStatus.COMPLETED
        assert order_2.order_status == OrderStatus.COMPLETED

