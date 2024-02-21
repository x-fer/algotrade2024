import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from game.tick import Ticker, GameData
from model import Game


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_just_finished():
    # Prepare
    game = Game(game_id=1, game_name="Test Game", start_time=datetime.now(), current_tick=10,
                total_ticks=10, is_finished=False, dataset_id=1, bots="", tick_time=1000, is_contest=False)
    ticker = Ticker()
    ticker.game_data[game.game_id] = GameData(game, {})

    # Execute
    with patch.object(Game, 'list') as mock_game_list:
        mock_game_list.return_value = [game]
        with patch.object(Game, 'update') as mock_game_update:
            await ticker.run_all_game_ticks()

    # Verify
    assert mock_game_update.call_count == 1
    mock_game_update.assert_called_with(game_id=game.game_id, is_finished=True)


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_not_started():
    # Prepare
    game = Game(game_id=2, game_name="Test Game 2", start_time=datetime.now() + timedelta(hours=1),
                current_tick=1, total_ticks=10, is_finished=False, dataset_id=1, bots="", tick_time=1000, is_contest=False)
    ticker = Ticker()
    ticker.game_data[game.game_id] = GameData(game, {})

    # Execute
    with patch.object(Game, 'list') as mock_game_list:
        mock_game_list.return_value = [game]
        await ticker.run_all_game_ticks()

    # Verify
    # Tick should not increase since the game has not started yet
    assert game.current_tick == 1


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_started():
    # Prepare
    game = Game(game_id=3, game_name="Test Game 3", start_time=datetime.now() - timedelta(hours=1),
                current_tick=1, total_ticks=10, is_finished=False, dataset_id=1, bots="", tick_time=1000, is_contest=False)
    ticker = Ticker()
    ticker.game_data[game.game_id] = GameData(game, {})

    # Execute
    with patch.object(Game, 'list') as mock_game_list:
        mock_game_list.return_value = [game]
        with patch.object(Ticker, 'run_game_tick') as mock_run_game_tick:
            await ticker.run_all_game_ticks()

    mock_run_game_tick.assert_called_once_with(game)

# if self.game_data.get(game.game_id) is None:
#                 self.game_data[game.game_id] = GameData(game, {})


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_data_not_exist():
    # Prepare
    game = Game(game_id=4, game_name="Test Game 4", start_time=datetime.now() - timedelta(hours=1),
                current_tick=1, total_ticks=10, is_finished=False, dataset_id=1, bots="", tick_time=1000, is_contest=False)
    ticker = Ticker()

    # Execute
    with patch.object(Game, 'list') as mock_game_list:
        mock_game_list.return_value = [game]
        with patch.object(Ticker, 'run_game_tick') as mock_run_game_tick:
            await ticker.run_all_game_ticks()

    # Verify
    assert game.game_id in ticker.game_data
    mock_run_game_tick.assert_called_once_with(game)

# if game.is_finished:
#     logger.info(f" {game.game_name} is finished")
#     continue


@pytest.mark.asyncio
async def test_run_all_game_ticks_game_finished():
    # Prepare
    game = Game(game_id=5, game_name="Test Game 5", start_time=datetime.now() - timedelta(hours=1),
                current_tick=10, total_ticks=10, is_finished=True, dataset_id=1, bots="", tick_time=1000, is_contest=False)
    ticker = Ticker()
    ticker.game_data[game.game_id] = GameData(game, {})

    # Execute
    with patch.object(Game, 'list') as mock_game_list:
        mock_game_list.return_value = [game]
        with patch.object(Ticker, 'run_game_tick') as mock_run_game_tick:
            await ticker.run_all_game_ticks()

    # Verify
    mock_run_game_tick.assert_not_called()
    assert game.current_tick == 10
    assert game.is_finished is True
    assert game.game_id in ticker.game_data
