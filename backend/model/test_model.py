from datetime import datetime
from model.order import Order
from model.order_types import OrderSide
from model.resource import Resource


def test_order_equal():
    order = Order(
        game_id = "1",
        player_id = "1",
        price = 1,
        size = 1,
        tick = 1,
        timestamp = datetime.now(),
        resource = Resource.COAL.value,
        order_side = OrderSide.BUY.value,
    )

    assert order.resource == Resource.COAL

    order.resource = Resource.OIL

    assert order.resource == Resource.OIL

    order.resource = Resource.BIOMASS

    assert order.resource == Resource.BIOMASS