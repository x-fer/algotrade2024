import pytest
from model import Game
from game.tick import Ticker
from unittest.mock import patch
from game.tick.tick_fixtures import *


@pytest.mark.asyncio
async def test_run_game_tick(
    sample_game, sample_game_data, tick_data,
):
    with patch.object(Ticker, 'get_tick_data', return_value=tick_data), \
            patch.object(Ticker, 'run_markets'), \
            patch.object(Ticker, 'run_power_plants'), \
            patch.object(Ticker, 'run_electricity_market', return_value=(tick_data, {})), \
            patch.object(Ticker, 'save_electricity_orders'), \
            patch.object(Ticker, 'save_tick_data'), \
            patch.object(Ticker, 'save_market_data'), \
            patch.object(Game, 'update'), \
            patch.object(Ticker, 'run_bots'):

        ticker = Ticker()
        ticker.game_data[sample_game.game_id] = sample_game_data

        await ticker.run_game_tick(sample_game)

        Ticker.get_tick_data.assert_called_once_with(sample_game)
        Ticker.run_markets.assert_called_once()
        Ticker.run_power_plants.assert_called_once()
        Ticker.run_electricity_market.assert_called_once()
        Ticker.save_electricity_orders.assert_called_once()
        Ticker.save_tick_data.assert_called_once()
        Game.update.assert_called_once_with(
            game_id=sample_game.game_id, current_tick=sample_game.current_tick + 1)
        Ticker.run_bots.assert_called_once_with(tick_data)
