from model import Order, Player, OrderSide, OrderStatus, ResourcesModel
from fixtures.fixtures import get_player_dict
from fixtures.fixtures import *


def test_when_transaction_successful(get_player, get_order, coal_market):
    player_1: Player = get_player(money=100, resources=ResourcesModel(coal=0))
    player_2: Player = get_player(money=0, resources=ResourcesModel(coal=100))
    order_1: Order = get_order(
        player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY, tick=1)
    order_2: Order = get_order(
        player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL, tick=1)
    order_3: Order = get_order(
        player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL, tick=1)
    player_dict = get_player_dict([player_1, player_2])

    coal_market.set_players(player_dict)

    updated = coal_market.match([order_1, order_2, order_3], 1)

    assert updated[order_1.order_id].order_status == OrderStatus.COMPLETED
    assert updated[order_2.order_id].order_status == OrderStatus.COMPLETED
    assert updated[order_3.order_id].order_status == OrderStatus.ACTIVE

    assert player_1.money == 0
    assert player_1.resources.coal == 100
    assert player_2.money == 100
    assert player_2.resources.coal == 0

    assert updated[order_1.order_id].filled_size == 100
    assert updated[order_1.order_id].filled_money == 100
    assert updated[order_1.order_id].filled_price == 1


def test_cancel_before_match(get_player, get_order, coal_market):
    player_1: Player = get_player(money=100, resources=ResourcesModel(coal=0))
    player_2: Player = get_player(money=0, resources=ResourcesModel(coal=100))
    order_1: Order = get_order(
        player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY, tick=1)
    order_2: Order = get_order(
        player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL, tick=1)
    order_3: Order = get_order(
        player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL, tick=1)
    player_dict = get_player_dict([player_1, player_2])

    coal_market.set_players(player_dict)

    updated = coal_market.match([order_1], 1)

    updated |= coal_market.cancel([order_1])
    updated |= coal_market.match([order_2, order_3], 1)

    assert updated[order_1.order_id].order_status == OrderStatus.CANCELLED
    assert updated[order_2.order_id].order_status == OrderStatus.ACTIVE
    assert updated[order_3.order_id].order_status == OrderStatus.ACTIVE

    assert player_1.money == 100
    assert player_1.resources.coal == 0
    assert player_2.money == 0
    assert player_2.resources.coal == 100

    assert updated[order_1.order_id].filled_size == 0
    assert updated[order_1.order_id].filled_money == 0
    assert updated[order_1.order_id].filled_price == 0


def test_user_low_balance(get_player, get_order, coal_market):
    player_1: Player = get_player(money=0, resources=ResourcesModel(coal=0))
    player_2: Player = get_player(money=0, resources=ResourcesModel(coal=100))
    order_1: Order = get_order(
        player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY, tick=1)
    order_2: Order = get_order(
        player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL, tick=1)
    order_3: Order = get_order(
        player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL, tick=1)
    player_dict = get_player_dict([player_1, player_2])

    coal_market.set_players(player_dict)

    updated = coal_market.match([order_1, order_2, order_3], 1)

    assert updated[order_1.order_id].order_status == OrderStatus.CANCELLED
    assert updated[order_2.order_id].order_status == OrderStatus.ACTIVE
    assert updated[order_3.order_id].order_status == OrderStatus.ACTIVE

    assert player_1.money == 0
    assert player_1.resources.coal == 0
    assert player_2.money == 0
    assert player_2.resources.coal == 100

    assert updated[order_1.order_id].filled_size == 0
    assert updated[order_1.order_id].filled_money == 0
    assert updated[order_1.order_id].filled_price == 0


def test_user_low_resources(get_player, get_order, coal_market):
    player_1: Player = get_player(money=100, resources=ResourcesModel(coal=0))
    player_2: Player = get_player(money=0, resources=ResourcesModel(coal=0))
    order_1: Order = get_order(
        player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY, tick=1)
    order_2: Order = get_order(
        player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL, tick=1)
    order_3: Order = get_order(
        player_id=player_2.player_id, price=5, size=100, order_side=OrderSide.SELL, tick=1)
    player_dict = get_player_dict([player_1, player_2])

    coal_market.set_players(player_dict)

    updated = coal_market.match([order_1, order_2, order_3], 1)

    assert updated[order_1.order_id].order_status == OrderStatus.ACTIVE
    assert updated[order_2.order_id].order_status == OrderStatus.CANCELLED
    assert updated[order_3.order_id].order_status == OrderStatus.ACTIVE

    assert player_1.money == 100
    assert player_1.resources.coal == 0
    assert player_2.money == 0
    assert player_2.resources.coal == 0

    assert updated[order_1.order_id].filled_size == 0
    assert updated[order_1.order_id].filled_money == 0
    assert updated[order_1.order_id].filled_price == 0
