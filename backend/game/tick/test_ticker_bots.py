import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from game.tick import Ticker, GameData
from model import Game
from game.bots import DummyBot, ResourceBot
from game.fixtures.fixtures import *
from model.team import Team


@pytest.mark.asyncio
async def test_run_bots(get_tick_data):
    # Create sample game
    game = Game(
        game_id=1,
        game_name="Sample Game",
        start_time=datetime(2024, 1, 1),
        current_tick=1,
        total_ticks=10,
        is_finished=False,
        dataset_id=1,
        bots="dummy:3",
        tick_time=1000,
        is_contest=False
    )
    players = {
        1: MagicMock(),
        2: MagicMock(),
        3: MagicMock()
    }

    # Create sample bots
    bots = [DummyBot(), DummyBot(), DummyBot()]
    # Mock the Bot.run method
    with patch.object(DummyBot, 'run') as mock_run:
        with patch.object(ResourceBot, 'run') as mock_run:

            # Create a Ticker instance
            ticker = Ticker()

            # Set the bots for the game
            ticker.game_data[game.game_id] = GameData(game, players)
            tick_data = get_tick_data(markets={}, players={})

            # Run the method being tested
            await ticker.run_bots(tick_data)

            # Assertions
            # Ensure Bot.run is called once for each bot
            assert mock_run.call_count == len(bots)
            # Ensure Bot.run is called with no arguments
            mock_run.assert_called_with(tick_data)
