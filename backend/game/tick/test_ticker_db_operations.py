from pprint import pprint
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from game.market.resource_market import ResourceMarket
from model import Order, OrderStatus, Resource
from model.dataset_data import DatasetData
from model.market import Market
from model.order_types import OrderSide, OrderType
from game.tick import Ticker, TickData
from tick.test_tick_fixtures import *


@pytest.mark.asyncio
async def test_get_tick_data(sample_game, sample_players, sample_pending_orders, sample_user_cancelled_orders, sample_dataset_row):
    # Setup ticker
    ticker = Ticker()
    ticker.game_data[sample_game.game_id] = GameData(
        sample_game, sample_players)

    # Mocking database interaction
    async def mock_list_players(*args, **kwargs):
        return [sample_players[1], sample_players[2]]

    async def mock_list_orders(*args, **kwargs):
        if kwargs.get('order_status') == OrderStatus.PENDING:
            return sample_pending_orders
        elif kwargs.get('order_status') == OrderStatus.USER_CANCELLED:
            return sample_user_cancelled_orders

    async def mock_get_dataset_data(*args, **kwargs):
        return sample_dataset_row

    with patch('model.Player.list', new=mock_list_players), patch('model.Order.list', new=mock_list_orders), patch('model.DatasetData.get', new=mock_get_dataset_data):
        # Execute get_tick_data method
        tick_data = await ticker.get_tick_data(sample_game)

        # Assertions
        assert len(tick_data.players) == 2
        # Assuming 2 pending orders in sample_pending_orders fixture
        assert len(tick_data.pending_orders) == 2
        # Assuming 2 user cancelled orders in sample_user_cancelled_orders fixture
        assert len(tick_data.user_cancelled_orders) == 2
        assert tick_data.dataset_row == sample_dataset_row
        # Assuming all resources have markets created
        assert len(tick_data.markets) == len(Resource)


@pytest.fixture
def sample_update_orders():
    return {1:
            Order(order_id=1, game_id=1, player_id=1, order_type=OrderType.LIMIT, order_side=OrderSide.SELL,
                  order_status=OrderStatus.CANCELLED, resource=Resource.coal, price=50, size=100, tick=1, timestamp=datetime.now()),
            2: Order(order_id=2, game_id=1, player_id=2, order_type=OrderType.LIMIT,
                     order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, resource=Resource.oil, price=50, size=100, tick=1, timestamp=datetime.now())
            }


@patch('model.Player.update')
@patch('model.Order.update')
@pytest.mark.asyncio
async def test_save_tick_data(mock_order_update, mock_player_update, ticker, sample_game, sample_players, sample_pending_orders, sample_user_cancelled_orders, sample_dataset_row, sample_update_orders):
    tick_data = TickData(
        game=sample_game,
        players=sample_players,
        pending_orders=sample_pending_orders,
        user_cancelled_orders=sample_user_cancelled_orders,
        dataset_row=sample_dataset_row,
        markets=[],
        bots="",
        updated_orders=sample_update_orders
    )

    await ticker.save_tick_data(tick_data)

    assert mock_player_update.call_count == len(sample_players)
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
            assert kwargs["order_type"] == OrderType.LIMIT
            assert kwargs["order_side"] == OrderSide.SELL
            # Check timestamp is a datetime object
            assert kwargs["timestamp"].__class__ == pd.Timestamp
            assert kwargs["order_status"] == OrderStatus.COMPLETED
            assert kwargs["size"] == expected_energy_sold
            assert kwargs["filled_size"] == expected_energy_sold
            assert kwargs["price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["tick"] == 1
            assert kwargs["filled_price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["expiration_tick"] == 1
            assert kwargs["resource"] == Resource.energy.value


@pytest.mark.asyncio
async def test_save_market_data(ticker, sample_game, tick_data, sample_players):
    for resource in Resource:
        price_tracker_mock = MagicMock()
        price_tracker_mock.get_low.return_value = 50
        price_tracker_mock.get_high.return_value = 60
        price_tracker_mock.get_open.return_value = 45
        price_tracker_mock.get_close.return_value = 55
        price_tracker_mock.get_market.return_value = 70

        tick_data.markets[resource.value] = ResourceMarket(
            resource, sample_players)
        tick_data.markets[resource.value].price_tracker = price_tracker_mock

    with patch('model.market.Market.create') as mock_create:
        await ticker.save_market_data(tick_data)

        assert mock_create.call_count == len(Resource)

        expected_calls = [
            call(game_id=sample_game.game_id, tick=1, resource=resource.value,
                 low=50, high=60, open=45, close=55, market=70)
            for resource in Resource
        ]
        pprint(expected_calls)
        pprint(mock_create.call_args_list)

        mock_create.assert_has_calls(expected_calls, any_order=True)
