from datetime import datetime
from fastapi import HTTPException

from game.bots.resource_bot import BuySellVolume, ResourceBot
from .bot import Bot
from .bots import Bots
import pytest
from model import Resource, OrderSide

from fixtures.fixtures import *
from .resource_bot import BuySellPrice, resource_wanted_sum, min_volume, max_volume, default_volume, min_price, max_price


class DummyBot_1(Bot):
    pass


class DummyBot_2(Bot):
    pass


@pytest.fixture()
def use_test_bots():
    old_bots = Bots.bots
    Bots.bots = {"test": DummyBot_1, "test_2": DummyBot_2}
    yield
    Bots.bots = old_bots


@pytest.fixture()
def use_preset_variables():
    from resource_bot import resource_wanted_sum
    old_resource_wanted_sum = resource_wanted_sum
    resource_wanted_sum = 100
    yield
    resource_wanted_sum = old_resource_wanted_sum


def test_parse_string_valid(use_test_bots):
    bots = Bots.parse_string("test: 5")
    assert len(bots) == 1
    assert bots[0][0] == "test"
    assert bots[0][1] == 5


def test_parse_string_valid_2(use_test_bots):
    bots = Bots.parse_string("test: 5; test_2: 1")
    assert len(bots) == 2
    assert bots[0][0] == "test"
    assert bots[0][1] == 5
    assert bots[1][0] == "test_2"
    assert bots[1][1] == 1


def test_parse_string_invalid(use_test_bots):
    with pytest.raises(HTTPException):
        Bots.parse_string("drummy: 5")

    with pytest.raises(HTTPException):
        Bots.parse_string("tes5")

    with pytest.raises(HTTPException):
        Bots.parse_string("test 5")

    with pytest.raises(HTTPException):
        Bots.parse_string("test: 5000")

    with pytest.raises(HTTPException):
        Bots.parse_string("test: -1")

    with pytest.raises(HTTPException):
        Bots.parse_string("test: 1;;")


def test_create_bots(use_test_bots):
    bots = Bots.create_bots("test: 4; test_2: 1")

    assert len(bots) == 5

    assert sum([isinstance(bot, DummyBot_1) for bot in bots]) == 4
    assert sum([isinstance(bot, DummyBot_2) for bot in bots]) == 1


class TestResourceBot:
    @pytest.mark.asyncio
    async def test_resource_bot_init(self):
        bot = ResourceBot()
        assert bot.player_id is None
        assert bot.last_buy_coeffs == {resource: 0.5 for resource in Resource}
        assert bot.last_sell_coeffs == {resource: 0.5 for resource in Resource}
        assert bot.last_tick is None

    def test_get_resources_sum(self, get_player, get_tick_data):
        bot = ResourceBot()
        p1 = get_player()
        p2 = get_player()
        for resource in Resource:
            p1[resource] = 5
            p2[resource] = 10
        players = get_player_dict([p1, p2])
        tick_data = get_tick_data(players=players)

        resource_sum = bot.get_resources_sum(tick_data)

        for resource in Resource:
            assert resource_sum[resource] == 15

    def test_get_volume(self):
        bot = ResourceBot()

        # Bot manje prodaje ako je previse resursa
        resource_sum = resource_wanted_sum + 10
        volume: BuySellVolume = bot.get_volume(resource_sum)
        assert_volumes(volume)
        assert volume.buy_volume > default_volume
        assert volume.sell_volume < default_volume

        # Bot vise prodaje ako je manjak resursa
        resource_sum = resource_wanted_sum - 10
        volume: BuySellVolume = bot.get_volume(resource_sum)
        assert_volumes(volume)
        assert volume.buy_volume < default_volume
        assert volume.sell_volume > default_volume

        resource_sum = resource_wanted_sum - 1000000
        volume: BuySellVolume = bot.get_volume(resource_sum)
        assert_volumes(volume)

        resource_sum = resource_wanted_sum + 1000000
        volume: BuySellVolume = bot.get_volume(resource_sum)
        assert_volumes(volume)

    def test_get_filled_perc(self):
        bot = ResourceBot()
        orders = [get_order(OrderSide.BUY, 10, 100),
                  get_order(OrderSide.BUY, 10, 100),
                  get_order(OrderSide.SELL, 20, 100)]

        buy_perc, sell_perc = bot.get_filled_perc(orders)

        assert buy_perc == 0.1
        assert sell_perc == 0.2

        buy_perc, sell_perc = bot.get_filled_perc([])

        assert buy_perc == 0
        assert sell_perc == 0

        orders = [get_order(OrderSide.BUY, 100, 100)]
        buy_perc, sell_perc = bot.get_filled_perc(orders)
        assert buy_perc == 1
        assert sell_perc == 0


@pytest.fixture
def bot():
    bot = ResourceBot()
    bot.last_buy_coeffs[Resource.coal] = 0.5
    bot.last_sell_coeffs[Resource.coal] = 0.5
    return bot


@pytest.fixture
def volume():
    return BuySellVolume(100, 100)


class TestGetPrice:
    def test_get_price_0_0(self, bot, volume):
        price = bot.get_price(Resource.coal, volume, 0, 0)
        assert_prices(bot, price)

    def test_get_price_0_1(self, bot, volume):
        price = bot.get_price(Resource.coal, volume, 0, 0)
        assert_prices(bot, price)

    def test_get_price_1_0(self, bot, volume):
        price = bot.get_price(Resource.coal, volume, 1, 0)
        assert_prices(bot, price)

    def test_get_price_2(self, bot, volume):
        price = bot.get_price(Resource.coal, volume, 1, 0.2)
        assert_prices(bot, price)
        price = bot.get_price(Resource.coal, volume, 0.5, 0.76)
        assert_prices(bot, price)
        price = bot.get_price(Resource.coal, volume, 0.3, 0.2)
        assert_prices(bot, price)


def assert_prices(bot: ResourceBot, price: BuySellPrice):
    assert min_price <= price.buy_price <= max_price
    assert min_price <= price.sell_price <= max_price
    assert 0 < price.buy_price
    assert 0 < price.sell_price
    assert 0 <= bot.last_buy_coeffs[Resource.coal] <= 1
    assert 0 <= bot.last_sell_coeffs[Resource.coal] <= 1
    assert bot.last_sell_coeffs[Resource.coal] >= bot.last_buy_coeffs[Resource.coal]


def get_order(order_side, filled_size, size):
    return Order(
        order_id=0, game_id=0, player_id=0, price=0,
        filled_size=filled_size, size=size, tick=0,
        timestamp=datetime.now(),
        order_side=order_side,
        resource=Resource.coal
    )


def assert_volumes(volume: BuySellVolume):
    assert min_volume <= volume.buy_volume <= max_volume
    assert min_volume <= volume.sell_volume <= max_volume
    assert 0 < volume.buy_volume
    assert 0 < volume.sell_volume
