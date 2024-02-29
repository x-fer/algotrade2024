from collections import defaultdict
from databases import Database
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from game.tick import Ticker, GameData
from model import Game
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_run_all_game_ticks():

    games = [Game(game_id=1, game_name="Game1", is_finished=False,
                  start_time=datetime.now(), current_tick=0, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.list', new=mock_game_list), \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):

        ticker = Ticker()

        await ticker.run_all_game_ticks(1)

        mock_start_game.assert_called_once_with(games[0])

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_finished():

    games = [Game(game_id=1, game_name="Game1", is_finished=True,
                  start_time=datetime.now(), current_tick=0, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.list', new=mock_game_list), \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):

        ticker = Ticker()

        await ticker.run_all_game_ticks(1)

        mock_start_game.assert_not_called()

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_not_started():

    games = [Game(game_id=1, game_name="Game1", is_finished=False,
                  start_time=datetime.now() + timedelta(seconds=10), current_tick=0, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.list', new=mock_game_list), \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):

        ticker = Ticker()

        await ticker.run_all_game_ticks(1)

        mock_start_game.assert_not_called()

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_end_game():

    games = [Game(game_id=1, game_name="Game1", is_finished=False,
                  start_time=datetime.now() - timedelta(seconds=1), current_tick=10, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.list', new=mock_game_list), \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):

        ticker = Ticker()

        await ticker.run_all_game_ticks(1)

        mock_start_game.assert_not_called()

        mock_end_game.assert_called_once_with(games[0])


@pytest.mark.asyncio
async def test_end_game():
    game = Game(game_id=1, game_name="Game1", is_finished=False,
                start_time=datetime.now() - timedelta(seconds=1), current_tick=10, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)

    ticker = Ticker()

    ticker.game_data[1] = Mock()
    ticker.game_futures[1] = Mock()

    mock_game_update = AsyncMock()

    with patch('model.Game.update', new=mock_game_update):

        await ticker.end_game(game)

        mock_game_update.assert_called_once_with(
            game_id=1, is_finished=True)

        assert 1 not in ticker.game_data

        ticker.game_futures[1].cancel.assert_called_once()


@pytest.mark.asyncio
async def test_start_game():
    game = Game(game_id=1, game_name="Game1", is_finished=False,
                start_time=datetime.now() - timedelta(seconds=1), current_tick=10, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)

    ticker = Ticker()

    ticker.game_data[1] = Mock()
    ticker.game_futures[1] = Mock()

    mock_game_update = AsyncMock()

    with patch('model.Game.update', new=mock_game_update) as mock_game_update, \
            patch('game.tick.Ticker.delete_all_running_bots') as mock_delete_all_running_bots, \
            patch('game.tick.Ticker.run_game') as mock_run_game:

        await ticker.start_game(game)

        mock_delete_all_running_bots.assert_called_once_with(1)

        assert 1 in ticker.game_data
        assert 1 in ticker.game_futures

        await ticker.game_futures[1]


@pytest.mark.asyncio
async def test_run_game():

    game = Game(game_id=1, game_name="Game1", is_finished=False,
                start_time=datetime.now() - timedelta(seconds=1), current_tick=9, total_ticks=10, dataset_id=1, tick_time=1000, is_contest=True)

    ticker = Ticker()

    with patch('model.Game.get') as mock_get, \
            patch('databases.Database.transaction') as mock_transaction, \
            patch('databases.Database.execute') as mock_execute, \
            patch('game.tick.Ticker.run_game_tick') as mock_run_game_tick, \
            patch('asyncio.sleep') as mock_sleep:

        mock_get.return_value = game

        ticker.run_game_tick = MagicMock()

        await ticker.run_game(game, iters=1)

        mock_get.assert_called_once_with(game_id=1)

        ticker.run_game_tick.assert_called_once_with(game)
