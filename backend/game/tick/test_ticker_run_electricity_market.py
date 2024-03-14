from fixtures.fixtures import get_player_dict
from fixtures.fixtures import *
from config import config


def test_successful(get_tick_data, ticker, get_player):

    player1 = get_player(money=0, coal=0, energy=10,  energy_price=100)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(markets=[],
                              players=player_dict,
                              energy_demand=100,
                              max_energy_price=100
                              )

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {player1.player_id: 10}


def test_player_price_too_high(get_tick_data, ticker, get_player):

    player1 = get_player(money=0, coal=0, energy=10,  energy_price=101)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(markets=[],
                              players=player_dict,
                              energy_demand=100,
                              max_energy_price=100
                              )

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {}


def test_player_over_max_demand(get_tick_data, ticker, get_player):
    demand = 100

    max_sold_per_player = int(config["max_energy_per_player"] * demand)

    player1 = get_player(
        money=0, coal=0, energy=max_sold_per_player + 1,  energy_price=99)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(markets=[],
                              players=player_dict,
                              energy_demand=demand,
                              max_energy_price=100
                              )

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {player1.player_id: max_sold_per_player}


def test_player_no_energy(get_tick_data, ticker, get_player):

    player1 = get_player(money=0, coal=0, energy=0,  energy_price=1)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(markets=[],
                              players=player_dict,
                              energy_demand=100,
                              max_energy_price=100
                              )

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {}


def test_demand_filled(get_tick_data, ticker, get_player):
    demand = 101

    players = [get_player(money=0, coal=0, energy=50,  energy_price=90),
               get_player(money=0, coal=0, energy=0,  energy_price=91),
               get_player(money=0, coal=0, energy=50,  energy_price=91),
               get_player(money=0, coal=0, energy=50,  energy_price=92),
               get_player(money=0, coal=0, energy=50,  energy_price=93),
               get_player(money=0, coal=0, energy=50,  energy_price=94),
               get_player(money=0, coal=0, energy=50,  energy_price=95),
               get_player(money=0, coal=0, energy=100000,  energy_price=100),
               ]

    max_per_player = int(demand * config["max_energy_per_player"])

    player_dict = get_player_dict(players)

    tick_data = get_tick_data(markets=[],
                              players=player_dict,
                              energy_demand=demand,
                              max_energy_price=100
                              )

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    sold = {}
    for player in sorted(players, key=lambda x: x.energy_price):
        to_sell = min(player.energy, demand, max_per_player)

        if to_sell == 0:
            continue

        demand -= to_sell

        player.money += to_sell * player.energy_price

        sold[player.player_id] = to_sell

        if demand == 0:
            break
    else:
        assert False, "Demand not filled"  # pragma: no cover

    assert energy_sold == sold
