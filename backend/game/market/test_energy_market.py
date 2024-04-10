import pytest
from model import Player
from fixtures.fixtures import get_player_dict
from fixtures.fixtures import *
from .energy_market import EnergyMarket
from . import energy_market


@pytest.fixture
def market():
    old_max_energy_per_player = energy_market.max_energy_per_player
    energy_market.max_energy_per_player = 1
    yield EnergyMarket()
    energy_market.max_energy_per_player = old_max_energy_per_player


def test_not_sell_when_too_high_price(market: EnergyMarket, get_player):
    player_1: Player = get_player(money=0, energy=100, energy_price=200)
    player_dict = get_player_dict([player_1])

    orders = market.match(player_dict, demand=100, max_price=100)

    assert player_1.money == 0
    assert len(orders) == 0


def test_not_sell_when_filled(market: EnergyMarket, get_player):
    player_1: Player = get_player(money=0, energy=100, energy_price=50)
    player_2: Player = get_player(money=0, energy=100, energy_price=60)
    player_dict = get_player_dict([player_1, player_2])

    orders = market.match(player_dict, demand=100, max_price=100)

    assert player_1.money == 100*50
    assert player_2.money == 0
    assert len(orders) == 1


def test_sell_partial(market: EnergyMarket, get_player):
    player_1: Player = get_player(money=0, energy=100, energy_price=50)
    player_2: Player = get_player(money=0, energy=100, energy_price=60)
    player_dict = get_player_dict([player_1, player_2])

    orders = market.match(player_dict, demand=150, max_price=100)

    assert player_1.money == 100*50
    assert player_2.money == 50*60
    assert len(orders) == 2


def test_monopoly(market: EnergyMarket, get_player):
    energy_market.max_energy_per_player = 0.5

    player_1: Player = get_player(money=0, energy=100, energy_price=30)
    player_2: Player = get_player(money=0, energy=100, energy_price=50)
    player_dict = get_player_dict([player_1, player_2])

    orders = market.match(player_dict, demand=100, max_price=100)

    assert player_1.money == 30*50
    assert player_2.money == 50*50
    assert len(orders) == 2


def test_sell_split_when_equal_price(market: EnergyMarket, get_player):
    player_1: Player = get_player(money=0, energy=50, energy_price=50)
    player_2: Player = get_player(money=0, energy=50, energy_price=50)
    player_3: Player = get_player(money=0, energy=100, energy_price=50)
    player_dict = get_player_dict([player_1, player_2, player_3])

    orders = market.match(player_dict, demand=100, max_price=100)

    print(orders)
    assert player_1.money == 25*50
    assert player_2.money == 25*50
    assert player_3.money == 50*50
    assert len(orders) == 3


def test_sell_split_when_equal_price_with_monopoly(market: EnergyMarket, get_player):
    energy_market.max_energy_per_player = 0.3

    player_1: Player = get_player(money=0, energy=100, energy_price=50)
    player_2: Player = get_player(money=0, energy=100, energy_price=50)
    player_dict = get_player_dict([player_1, player_2])

    orders = market.match(player_dict, demand=100, max_price=100)

    assert player_1.money == 30*50
    assert player_2.money == 30*50
    assert len(orders) == 2