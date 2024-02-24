import pytest
from game.tick.ticker import GameData
from tick import Ticker, TickData
from model import Game, Player, PowerPlantType, Resource, DatasetData

from .test_tick_fixtures import sample_game, sample_players, ticker, sample_dataset_row, tick_data

import pytest
from model import PowerPlantType
from game.tick import TickData, Ticker

# Test case using fixtures


@pytest.mark.asyncio
async def test_run_power_plants(sample_game, sample_players, tick_data, sample_dataset_row):
    ticker = Ticker()
    ticker.game_data[sample_game.game_id] = GameData(
        sample_game, sample_players)
    tick_data.dataset_row = sample_dataset_row

    updated_tick_data = ticker.run_power_plants(tick_data)

    for player_id, player in updated_tick_data.players.items():
        total_energy = sum([
            player[plant_type.name.lower() + "_plants_powered"] *
            plant_type.get_produced_energy(updated_tick_data.dataset_row)
            for plant_type in PowerPlantType
        ])
        assert player.energy == total_energy
