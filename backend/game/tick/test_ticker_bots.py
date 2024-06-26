import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from game.tick import Ticker, GameData
from model import Game
from game.bots import ResourceBot
from fixtures.fixtures import *
from game.bots import ResourceBot
from fixtures.fixtures import *


@pytest.mark.asyncio
async def test_run_bots(get_tick_data):
    game = Game(
        game_id=1,
        game_name="Sample Game",
        start_time=datetime(2024, 1, 1),
        current_tick=1,
        total_ticks=10,
        is_finished=False,
        dataset_id=1,
        bots="resource_bot:3",
        tick_time=1000,
        is_contest=False
    )
    players = {
        1: MagicMock(),
        2: MagicMock(),
        3: MagicMock()
    }

    with patch.object(ResourceBot, 'run') as mock_run:
        ticker = Ticker()

        ticker.game_data[game.game_id] = GameData(game)
        tick_data = get_tick_data(markets={}, players=players)

        pipe = MagicMock()

        ticker.game_data[game.game_id].bot.run(pipe, tick_data)

        assert mock_run.call_count == 1
        mock_run.assert_called_with(pipe, tick_data)
