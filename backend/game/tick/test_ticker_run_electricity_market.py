from copy import deepcopy
from pprint import pprint
import pytest
from game.tick import TickData
from game.fixtures.fixtures import *
from model.order_types import OrderSide, OrderStatus
from model.player import Player
from config import config

# def run_electricity_market(self, tick_data: TickData, energy_market: EnergyMarket) -> Tuple[TickData, dict[int, int]]:
#         energy_sold = energy_market.match(
#             tick_data.players, tick_data.dataset_row["ENERGY_DEMAND"], tick_data.dataset_row["MAX_ENERGY_PRICE"])

#         return tick_data, energy_sold

# class EnergyMarket:
#     def match(self, players: dict[int, Player], demand: int, max_price: int) -> dict[int, int]:
#         players_sorted = sorted(players.values(), key=lambda x: x.energy_price)
#         players_sorted = [
#             player for player in players_sorted if player.energy_price <= max_price]

#         max_per_player = config["max_energy_per_player"]

#         orders = {}

#         for player in players_sorted:
#             to_sell = min(player.energy, demand, int(demand * max_per_player))

#             if to_sell == 0:
#                 continue

#             # player.energy -= to_sell # ne trebamo, zelimo da im se prikaze koliko proizvode
#             demand -= to_sell

#             player.money += to_sell * player.energy_price

#             orders[player.player_id] = to_sell

#             if demand == 0:
#                 break

#         return orders


def test_successful(get_tick_data, get_ticker, get_player, get_power_plant):

    player1 = get_player(money=0, coal=0, energy=10,  energy_price=100)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(power_plants={},
                              markets=[],
                              players=player_dict,
                              dataset_row={"ENERGY_DEMAND": 100, "MAX_ENERGY_PRICE": 100})

    ticker = get_ticker(player_dict)

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {player1.player_id: 10}


def test_player_price_too_high(get_tick_data, get_ticker, get_player, get_power_plant):

    player1 = get_player(money=0, coal=0, energy=10,  energy_price=101)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(power_plants={},
                              markets=[],
                              players=player_dict,
                              dataset_row={"ENERGY_DEMAND": 100, "MAX_ENERGY_PRICE": 100})

    ticker = get_ticker(player_dict)

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {}


def test_player_over_max_demand(get_tick_data, get_ticker, get_player, get_power_plant):
    demand = 100

    max_sold_per_player = int(config["max_energy_per_player"] * demand)

    player1 = get_player(
        money=0, coal=0, energy=max_sold_per_player + 1,  energy_price=99)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(power_plants={},
                              markets=[],
                              players=player_dict,
                              dataset_row={"ENERGY_DEMAND": demand, "MAX_ENERGY_PRICE": 100})

    ticker = get_ticker(player_dict)

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {player1.player_id: max_sold_per_player}


def test_player_no_energy(get_tick_data, get_ticker, get_player, get_power_plant):

    player1 = get_player(money=0, coal=0, energy=0,  energy_price=1)
    player_dict = get_player_dict([player1])

    tick_data = get_tick_data(power_plants={},
                              markets=[],
                              players=player_dict,
                              dataset_row={"ENERGY_DEMAND": 100, "MAX_ENERGY_PRICE": 100})

    ticker = get_ticker(player_dict)

    tick_data, energy_sold = ticker.run_electricity_market(
        tick_data, EnergyMarket())

    assert energy_sold == {}


def test_demand_filled(get_tick_data, get_ticker, get_player, get_power_plant):
    demand = 101

    players = [get_player(money=0, coal=0, energy=50,  energy_price=90),
               get_player(money=0, coal=0, energy=50,  energy_price=91),
               get_player(money=0, coal=0, energy=50,  energy_price=92),
               get_player(money=0, coal=0, energy=50,  energy_price=93),
               get_player(money=0, coal=0, energy=50,  energy_price=94),
               get_player(money=0, coal=0, energy=50,  energy_price=95),
               get_player(money=0, coal=0, energy=100000,  energy_price=100),
               ]

    max_per_player = int(demand * config["max_energy_per_player"])

    player_dict = get_player_dict(players)

    tick_data = get_tick_data(power_plants={},
                              markets=[],
                              players=player_dict,
                              dataset_row={"ENERGY_DEMAND": demand, "MAX_ENERGY_PRICE": 100})

    ticker = get_ticker(player_dict)

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
        assert False, "Demand not filled"

    assert energy_sold == sold
