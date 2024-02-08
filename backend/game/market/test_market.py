from model import Order, Player, OrderSide, OrderStatus, ContractStatus
from . import ResourceMarket, TickMarketData, EnergyMarket
from game.fixtures.fixtures import *


class TestResourceMarket():
    def test_when_transaction_successful(self, game, get_player, get_order, coal_market: ResourceMarket):
        player_1: Player = get_player(money=100, coal=0)
        player_2: Player = get_player(money=0, coal=100)
        order_1: Order = get_order(player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY)
        order_2: Order = get_order(player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL)
        order_3: Order = get_order(player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL)
        players = get_player_dict([player_1, player_2])

        tick_data = TickMarketData(game=game, players=players)
        coal_market.init_tick_data(tick_data)
        coal_market.orderbook.add_order(order_3)
        coal_market.orderbook.match(1)

        tick_data = TickMarketData(game=game, players=players)
        coal_market.init_tick_data(tick_data)
        coal_market.orderbook.add_order(order_1)
        coal_market.orderbook.add_order(order_2)
        coal_market.orderbook.match(1)

        assert player_1.money == 0
        assert player_1.coal == 100
        assert player_2.money == 100
        assert player_2.coal == 0
        assert order_1.order_id in tick_data.updated_orders
        assert order_2.order_id in tick_data.updated_orders
        assert order_3.order_id not in tick_data.updated_orders
        assert tick_data.updated_orders[order_1.order_id] is order_1
        assert tick_data.updated_orders[order_2.order_id] is order_2
        assert order_1.order_status == OrderStatus.COMPLETED
        assert order_2.order_status == OrderStatus.COMPLETED


class TestEnergMarket():
    def test_when_player_has_no_money(self, game, get_player, get_order, energy_market: EnergyMarket):
        player: Player = get_player(money=0)
        bot: Player = get_player(money=100)
        order_1: Order = get_order(player_id=bot.player_id, price=1, size=100, order_side=OrderSide.BUY)
        order_2: Order = get_order(player_id=player.player_id, price=1, size=100, order_side=OrderSide.SELL)
        players = get_player_dict([player, bot])

        tick_data = TickMarketData(game=game, players=players)
        energy_market.init_tick_data(tick_data)
        energy_market.orderbook.add_order(order_1)
        energy_market.orderbook.add_order(order_2)
        energy_market.orderbook.match(1)

        assert player.money == 0
        assert bot.money == 100
        assert order_1.order_status == OrderStatus.ACTIVE
        assert order_2.order_status == OrderStatus.CANCELLED
        assert len(tick_data.new_contracts) == 0

    def test_when_player_has_money(self, game, get_player, get_order, energy_market: EnergyMarket):
        player: Player = get_player(money=100)
        bot: Player = get_player(money=100)
        order_1: Order = get_order(player_id=bot.player_id, price=1, size=100, order_side=OrderSide.BUY)
        order_2: Order = get_order(player_id=player.player_id, price=1, size=100, order_side=OrderSide.SELL)
        players = get_player_dict([player, bot])

        tick_data = TickMarketData(game=game, players=players)
        energy_market.init_tick_data(tick_data)
        energy_market.orderbook.add_order(order_1)
        energy_market.orderbook.add_order(order_2)
        energy_market.orderbook.match(1)

        assert player.money < 100
        assert bot.money == 0
        assert order_1.order_status == OrderStatus.COMPLETED
        assert order_2.order_status == OrderStatus.COMPLETED
        assert len(tick_data.new_contracts) == 1
        assert tick_data.new_contracts[0].bot_id == bot.player_id
        assert tick_data.new_contracts[0].player_id == player.player_id
        assert tick_data.new_contracts[0].contract_status == ContractStatus.ACTIVE
        assert tick_data.new_contracts[0].size == 100
        assert tick_data.new_contracts[0].price == 100
    