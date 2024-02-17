from copy import deepcopy
from pprint import pprint
import pytest
from game.tick import TickData
from game.fixtures.fixtures import *
from model.order_types import OrderSide, OrderStatus
from model.player import Player


def test_run_power_plants_no_resource(get_tick_data, get_ticker, get_player, get_power_plant):

    player1 = get_player(money=1000, coal=0, energy=0)
    player_dict = get_player_dict([player1])

    power_plant1 = get_power_plant(
        player_id=player1.player_id, type=PowerPlantType.COAL, powered_on=True)

    tick_data = get_tick_data(power_plants={
                              player1.player_id: [power_plant1]},
                              markets=[],
                              players=player_dict)

    ticker = get_ticker(players=player_dict)

    ticker.run_power_plants(tick_data)

    assert player1.energy == 0
    assert power_plant1.temperature == 0.0
    assert power_plant1.powered_on == False


def test_run_power_plants_heating_up(get_tick_data, get_ticker, get_player, get_power_plant):

    player1 = get_player(money=1000, coal=1, energy=0)
    player_dict = get_player_dict([player1])

    power_plant1 = get_power_plant(
        player_id=player1.player_id, type=PowerPlantType.COAL, powered_on=True)

    tick_data = get_tick_data(power_plants={
                              player1.player_id: [power_plant1]},
                              markets=[],
                              players=player_dict)

    ticker = get_ticker(players=player_dict)

    ticker.run_power_plants(tick_data)

    assert player1.energy == 0
    assert player1.coal == 0
    assert power_plant1.temperature == PowerPlantType.COAL.get_new_temp(
        0.0, True)
    assert power_plant1.powered_on == True


def test_run_power_plants_producing(get_tick_data, get_ticker, get_player, get_power_plant):
    player1 = get_player(money=1000, coal=1, energy=0)
    player_dict = get_player_dict([player1])

    power_plant1 = get_power_plant(
        player_id=player1.player_id, type=PowerPlantType.COAL, powered_on=True, temperature=1.0)

    tick_data = get_tick_data(power_plants={
        player1.player_id: [power_plant1]},
        markets=[],
        players=player_dict)

    ticker = get_ticker(players=player_dict)

    ticker.run_power_plants(tick_data)

    assert player1.energy == power_plant1.get_produced_energy(
        tick_data.dataset_row)
    assert player1.coal == 0
    assert power_plant1.temperature == PowerPlantType.COAL.get_new_temp(
        1.0, True)
    assert power_plant1.powered_on == True


def test_run_power_plants_renewable(get_tick_data, get_ticker, get_player, get_power_plant):
    player1 = get_player(money=0, energy=0)
    player_dict = get_player_dict([player1])

    power_plant1 = get_power_plant(
        player_id=player1.player_id, type=PowerPlantType.WIND, powered_on=True, temperature=1.0)

    tick_data = get_tick_data(power_plants={
        player1.player_id: [power_plant1]},
        markets=[],
        players=player_dict)

    ticker = get_ticker(players=player_dict)

    ticker.run_power_plants(tick_data)

    assert player1.energy == power_plant1.get_produced_energy(
        tick_data.dataset_row)
    assert power_plant1.temperature == PowerPlantType.WIND.get_new_temp(
        1.0, True)
    assert power_plant1.powered_on == True
