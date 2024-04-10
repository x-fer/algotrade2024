import pytest
from game.bots.resource_bot import ResourceBot
from model import Game
from game.tick import Ticker
from unittest.mock import patch
from game.tick.tick_fixtures import *


def test_run_game_tick(
    sample_game, sample_game_data, tick_data,
):
    with patch.object(Ticker, 'get_tick_data', return_value=tick_data), \
            patch.object(Ticker, 'run_markets'), \
            patch.object(Ticker, 'run_power_plants'), \
            patch.object(Ticker, 'run_electricity_market', return_value=(tick_data, {})), \
            patch.object(Ticker, 'save_electricity_orders'), \
            patch.object(Ticker, 'save_tick_data'), \
            patch.object(Ticker, 'save_market_data'), \
            patch.object(Ticker, '_log_networth'), \
            patch.object(Game, 'get', return_value=sample_game), \
            patch.object(Game, 'update'), \
            patch.object(Game, 'save'), \
            patch.object(ResourceBot, 'run'), \
            patch.object(Ticker, 'get_players_and_enter_context') as find_player:

        find_player.return_value = tick_data.players
        ticker = Ticker()
        ticker.game_data[sample_game.game_id] = sample_game_data
        old_tick = sample_game.current_tick

        ticker.run_game_tick(sample_game)

        assert sample_game.current_tick == old_tick + 1
        Ticker.get_tick_data.assert_called_once_with(sample_game, tick_data.players)
        Ticker.run_markets.assert_called_once()
        Ticker.run_power_plants.assert_called_once()
        Ticker.run_electricity_market.assert_called_once()
        Ticker.save_electricity_orders.assert_called_once()
        Ticker.save_tick_data.assert_called_once()
        Game.update.assert_called_once_with(is_finished=False)
        Game.save.assert_called_once()
        ResourceBot.run.assert_called_once()
