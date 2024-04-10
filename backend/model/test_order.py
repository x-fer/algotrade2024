from datetime import datetime

import pytest

from model import Order, OrderSide, OrderStatus, OrderType, Resource


@pytest.fixture
def sample_order():
    return Order(
        order_id=1,
        game_id=1,
        player_id=1,
        price=50,
        size=100,
        tick=1,
        timestamp=datetime.now(),
        order_side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        order_status=OrderStatus.PENDING,
        filled_size=0,
        filled_money=0,
        filled_price=0,
        expiration_tick=1,
        resource=Resource.coal
    )


def test_order_initialization(sample_order):
    assert sample_order.order_id == 1
    assert sample_order.game_id == 1
    assert sample_order.player_id == 1
    assert sample_order.price == 50
    assert sample_order.size == 100
    assert sample_order.tick == 1
    assert isinstance(sample_order.timestamp, datetime)
    assert sample_order.order_side == OrderSide.BUY
    assert sample_order.order_type == OrderType.LIMIT
    assert sample_order.order_status == OrderStatus.PENDING
    assert sample_order.filled_size == 0
    assert sample_order.filled_money == 0
    assert sample_order.filled_price == 0
    assert sample_order.expiration_tick == 1
    assert sample_order.resource == Resource.coal


def test_order_comparison(sample_order):
    order_1 = sample_order
    order_2 = sample_order
    assert order_1 == order_2


def test_order_hashing(sample_order):
    order_set = {sample_order}
    assert sample_order in order_set
