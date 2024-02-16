import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from game.tick.ticker import GameData
from model import Player, PowerPlant, Game, Order, OrderStatus, Resource
from model.order_types import OrderSide, OrderType
from tick import Ticker, TickData
from tick.test_tick_fixtures import *


@patch('model.Player.list')
@patch('model.PowerPlant.list')
@patch('model.Order.list')
@patch('model.DatasetData.get')
@pytest.mark.asyncio
async def test_get_tick_data(mock_dataset_get, mock_order_list, mock_powerplant_list, mock_player_list, ticker, sample_game, sample_players, sample_power_plants, sample_pending_orders, sample_user_cancelled_orders, sample_dataset_row):
    mock_player_list.return_value = sample_players.values()
    mock_powerplant_list.side_effect = lambda player_id: sample_power_plants[player_id]
    mock_order_list.side_effect = lambda **kwargs: sample_pending_orders if kwargs.get(
        "order_status") == OrderStatus.PENDING else sample_user_cancelled_orders
    mock_dataset_get.return_value = sample_dataset_row

    tick_data = await ticker.get_tick_data(sample_game)

    assert len(tick_data.players) == len(sample_players)
    assert len(tick_data.power_plants) == len(sample_power_plants)
    assert len(tick_data.pending_orders) == len(sample_pending_orders)
    assert len(tick_data.user_cancelled_orders) == len(
        sample_user_cancelled_orders)
    assert tick_data.dataset_row == sample_dataset_row


@pytest.fixture
def sample_update_orders():
    return {1:
            Order(order_id=1, game_id=1, player_id=1, order_type=OrderType.LIMIT, order_side=OrderSide.SELL,
                  order_status=OrderStatus.CANCELLED, resource=Resource.coal, price=50, size=100, tick=1, timestamp=datetime.now()),
            2: Order(order_id=2, game_id=1, player_id=2, order_type=OrderType.LIMIT,
                     order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, resource=Resource.oil, price=50, size=100, tick=1, timestamp=datetime.now())
            }


@patch('model.Player.update')
@patch('model.PowerPlant.update')
@patch('model.Order.update')
@pytest.mark.asyncio
async def test_save_tick_data(mock_order_update, mock_powerplant_update, mock_player_update, ticker, sample_game, sample_players, sample_power_plants, sample_pending_orders, sample_user_cancelled_orders, sample_dataset_row, sample_update_orders):
    tick_data = TickData(
        game=sample_game,
        players=sample_players,
        power_plants=sample_power_plants,
        pending_orders=sample_pending_orders,
        user_cancelled_orders=sample_user_cancelled_orders,
        dataset_row=sample_dataset_row,
        markets=[],
        bots="",
        updated_orders=sample_update_orders
    )

    await ticker.save_tick_data(sample_game, tick_data)

    assert mock_player_update.call_count == len(sample_players)
    assert mock_powerplant_update.call_count == len(sample_power_plants[1]) + len(
        sample_power_plants[2])
    assert mock_order_update.call_count == len(sample_update_orders)


@pytest.mark.asyncio
async def test_save_electricity_orders(sample_game, sample_players):
    players = sample_players
    game = sample_game
    energy_sold = {1: 100, 2: 200}
    # Mock the Order.create method
    with patch('model.Order.create') as mock_order_create:
        # Create a Ticker instance
        ticker = Ticker()

        # Run the method being tested
        await ticker.save_electricity_orders(players, game, energy_sold, 1)

        # Assertions
        assert mock_order_create.call_count == 2  # Called once for each player
        expected_calls = [
            ((1,),),  # Check arguments passed to Order.create for Player 1
            ((2,),),  # Check arguments passed to Order.create for Player 2
        ]
        for call_args, expected_energy_sold in zip(mock_order_create.call_args_list, energy_sold.values()):
            args, kwargs = call_args
            assert args == ()  # No positional arguments
            assert kwargs["game_id"] == game.game_id
            assert kwargs["order_type"] == OrderType.LIMIT.value
            assert kwargs["order_side"] == OrderSide.SELL.value
            # Check timestamp is a datetime object
            assert kwargs["timestamp"].__class__ == pd.Timestamp
            assert kwargs["order_status"] == OrderStatus.COMPLETED.value
            assert kwargs["size"] == expected_energy_sold
            assert kwargs["filled_size"] == expected_energy_sold
            assert kwargs["price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["tick"] == 1
            assert kwargs["filled_price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["expiration_tick"] == 1
            assert kwargs["resource"] == Resource.energy.value
