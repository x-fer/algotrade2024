import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from game.tick import Ticker
from model import Game
from unittest.mock import Mock
from fixtures.fixtures import *
import tracemalloc

from routers.users.fixtures import set_mock_find


tracemalloc.start()


@pytest.fixture
def ticker():
    return Ticker()


def get_game(start_time, current_tick, total_ticks, is_finished):
    return Game(pk="1", game_name="Game1",
                is_finished=is_finished,
                start_time=start_time,
                current_tick=current_tick,
                total_ticks=total_ticks,
                dataset_id=1,
                tick_time=1000, is_contest=True)


@pytest.mark.asyncio
async def test_run_tick_manager(ticker):
    games = [get_game(start_time=datetime.now(), current_tick=0,
                      total_ticks=10, is_finished=False)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.find') as find_mock, \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):
        set_mock_find(find_mock, "all", mock_game_list)

        await ticker.run_tick_manager(1)

        # mock_start_game.assert_called_once_with([games[0], None])

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_run_tick_manager_game_finished(ticker):
    games = [get_game(start_time=datetime.now(), current_tick=0,
                      total_ticks=10, is_finished=True)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.find') as find_mock, \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):
        set_mock_find(find_mock, "all", mock_game_list)
        await ticker.run_tick_manager(1)

        mock_start_game.assert_not_called()

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_run_tick_manager_game_not_started(ticker):
    games = [get_game(start_time=datetime.now() + timedelta(seconds=10),
                      current_tick=0, total_ticks=10, is_finished=False)]
    mock_game_list = AsyncMock(return_value=games)

    mock_start_game = AsyncMock()
    mock_end_game = AsyncMock()

    with patch('model.Game.find') as find_mock, \
            patch('game.tick.Ticker.start_game', new=mock_start_game), \
            patch('game.tick.Ticker.end_game', new=mock_end_game):
        set_mock_find(find_mock, "all", mock_game_list)

        await ticker.run_tick_manager(1)

        mock_start_game.assert_not_called()

        mock_end_game.assert_not_called()


@pytest.mark.asyncio
async def test_end_game(ticker):
    game = get_game(start_time=datetime.now() - timedelta(seconds=1),
                    current_tick=10, total_ticks=10, is_finished=False)

    ticker.game_data["1"] = Mock()
    ticker.game_futures["1"] = Mock()

    mock_game_save = Mock()

    with patch('model.Game.save', new=mock_game_save), patch("game.tick.Ticker._log_networth"):
        await ticker.end_game(game)

        assert game.is_finished

        assert "1" not in ticker.game_data

        ticker.game_futures["1"].cancel.assert_called_once()


@pytest.mark.asyncio
async def test_start_game(ticker):
    game = get_game(start_time=datetime.now() - timedelta(seconds=1),
                    current_tick=10, total_ticks=10, is_finished=False)

    with patch('game.tick.Ticker.delete_all_running_bots') as delete_all_running_bots_mock, \
            patch('game.tick.Ticker.load_previous_oderbook') as load_previous_oderbook_mock, \
            patch('game.tick.Ticker.run_game') as run_game_mock:
        await ticker.start_game(game)

        delete_all_running_bots_mock.assert_called_once_with("1")
        run_game_mock.assert_called_once()
        load_previous_oderbook_mock.assert_called_once()

        assert game.game_id in ticker.game_data
        assert game.game_id in ticker.game_futures


@pytest.mark.asyncio
async def test_run_game(ticker):
    game = get_game(start_time=datetime.now() - timedelta(seconds=1),
                    current_tick=9, total_ticks=10, is_finished=False)

    with patch('model.Game.get', return_value=game) as mock_get, \
            patch('game.tick.Ticker.run_game_tick') as mock_run_game_tick, \
            patch('asyncio.sleep') as mock_sleep:

        ticker.run_game_tick = MagicMock()

        await ticker.run_game(game, iters=1)

        mock_get.assert_called_once_with("1")

        ticker.run_game_tick.assert_called_once_with(game)
