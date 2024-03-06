from pprint import pprint
import pandas as pd
from game.price_tracker.price_tracker import PriceTracker
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from game.market.resource_market import ResourceMarket
from model import Order, OrderStatus, Resource, OrderSide, OrderType
from game.tick import Ticker, TickData
from model.resource import Energy
from game.tick.tick_fixtures import *


@pytest.mark.asyncio
async def test_get_tick_data(sample_game, sample_players, 
                             sample_pending_orders, sample_user_cancelled_orders, 
                             sample_dataset_row, sample_game_data):
    ticker = Ticker()
    ticker.game_data[sample_game.game_id] = sample_game_data

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
        tick_data = await ticker.get_tick_data(sample_game)

        assert len(tick_data.players) == 2
        assert len(tick_data.pending_orders) == 2
        assert len(tick_data.user_cancelled_orders) == 2
        assert tick_data.dataset_row == sample_dataset_row
        assert len(tick_data.markets) == len(Resource)


@patch('model.Player.update_many')
@patch('model.Order.update_many')
@pytest.mark.asyncio
async def test_save_tick_data(mock_order_update_many, 
                              mock_player_update_many, 
                              ticker: Ticker, sample_game, sample_players, 
                              sample_pending_orders, sample_user_cancelled_orders, 
                              sample_dataset_row, 
                              sample_energy_market):
    sample_update_orders = {
        1: Order(order_id=1, game_id=1, player_id=1,
                 order_type=OrderType.LIMIT,
                 order_side=OrderSide.SELL,
                 order_status=OrderStatus.CANCELLED,
                 resource=Resource.coal,
                 price=50, size=100, tick=1,
                 timestamp=datetime.now()),
        2: Order(order_id=2, game_id=1, player_id=2,
                 order_type=OrderType.LIMIT,
                 order_side=OrderSide.BUY,
                 order_status=OrderStatus.ACTIVE,
                 resource=Resource.oil,
                 price=50, size=100, tick=1,
                 timestamp=datetime.now())}

    tick_data = TickData(
        game=sample_game,
        players=sample_players,
        pending_orders=sample_pending_orders,
        user_cancelled_orders=sample_user_cancelled_orders,
        dataset_row=sample_dataset_row,
        markets=[],
        bots="",
        updated_orders=sample_update_orders,
        energy_market=sample_energy_market
    )

    await ticker.save_tick_data(tick_data)

    assert mock_player_update_many.call_count == 1
    assert mock_order_update_many.call_count == 1


@pytest.mark.asyncio
async def test_save_electricity_orders(sample_game, sample_players):
    players = sample_players
    game = sample_game
    energy_sold = {1: 100, 2: 200}
    with patch('model.Order.create') as mock_order_create:
        ticker = Ticker()

        await ticker.save_electricity_orders(
            players=players, game=game, energy_sold=energy_sold, tick=1)

        assert mock_order_create.call_count == 2

        for call_args, expected_energy_sold in zip(mock_order_create.call_args_list, energy_sold.values()):
            args, kwargs = call_args
            assert args == ()
            assert kwargs["game_id"] == game.game_id
            assert kwargs["order_type"] == OrderType.LIMIT
            assert kwargs["order_side"] == OrderSide.SELL
            assert kwargs["timestamp"].__class__ == pd.Timestamp
            assert kwargs["order_status"] == OrderStatus.COMPLETED
            assert kwargs["size"] == expected_energy_sold
            assert kwargs["filled_size"] == expected_energy_sold
            assert kwargs["price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["tick"] == 1
            assert kwargs["filled_price"] == players[kwargs["player_id"]].energy_price
            assert kwargs["expiration_tick"] == 1
            assert kwargs["resource"] == Energy.energy.value


@pytest.mark.asyncio
async def test_save_market_data(ticker: Ticker, sample_game, tick_data):
    for resource in Resource:
        price_tracker_mock: PriceTracker = MagicMock()
        price_tracker_mock.get_low.return_value = 50
        price_tracker_mock.get_high.return_value = 60
        price_tracker_mock.get_open.return_value = 45
        price_tracker_mock.get_close.return_value = 55
        price_tracker_mock.get_average.return_value = 70
        price_tracker_mock.get_volume.return_value = 20

        tick_data.markets[resource.value] = ResourceMarket(resource)
        tick_data.markets[resource.value].price_tracker = price_tracker_mock

    with patch('model.market.Market.create') as mock_create:
        await ticker.save_market_data(tick_data)

        assert mock_create.call_count == len(Resource) + 1

        expected_calls = [
            call(game_id=sample_game.game_id, tick=1, resource=resource.value,
                 low=50, high=60, open=45, close=55, market=70, volume=20)
            for resource in Resource
        ]

        mock_create.assert_has_calls(expected_calls, any_order=True)
