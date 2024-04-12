from game.price_tracker.price_tracker import PriceTracker
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from game.market.resource_market import ResourceMarket
from model import Order, OrderStatus, Resource, OrderSide
from game.tick import Ticker, TickData
from game.tick.tick_fixtures import *
from model.market import Market
from routers.users.fixtures import set_mock_find


def test_get_tick_data(
    sample_game,
    sample_players_list,
    sample_players,
    sample_pending_orders,
    sample_user_cancelled_orders,
    sample_dataset_row,
    sample_game_data,
):
    ticker = Ticker()
    ticker.game_data[sample_game.game_id] = sample_game_data

    def mock_list_players(*args, **kwargs):
        return sample_players_list

    called_times = 0
    def mock_list_orders(*args, **kwargs):
        nonlocal called_times
        called_times += 1
        if called_times == 1:
            return sample_pending_orders
        elif called_times == 2:
            return sample_user_cancelled_orders
        raise Exception()

    with patch("model.Player.find", return_value=MagicMock(side_effect=mock_list_players)), patch(
        "model.Order.find") as order_find_mock, patch("model.DatasetData.find") as dataset_data_find_mock:
        
        order_find_mock.return_value = MagicMock()
        order_find_mock.return_value.all = MagicMock(side_effect=mock_list_orders)
        set_mock_find(dataset_data_find_mock, "first", sample_dataset_row)
        tick_data = ticker.get_tick_data(sample_game, sample_players)

        assert len(tick_data.players) == 2
        assert len(tick_data.pending_orders) == 2
        assert len(tick_data.user_cancelled_orders) == 2
        assert tick_data.dataset_row == sample_dataset_row
        assert len(tick_data.markets) == len(Resource)


@patch("model.Player.save")
@patch("model.Order.save")
def test_save_tick_data(
    mock_order_save,
    mock_player_save,
    ticker: Ticker,
    sample_game,
    sample_players,
    sample_pending_orders,
    sample_user_cancelled_orders,
    sample_dataset_row,
    sample_energy_market,
):
    sample_update_orders = {
        "1": Order(
            pk="1",
            game_id="1",
            player_id="1",
            order_side=OrderSide.SELL.value,
            order_status=OrderStatus.CANCELLED.value,
            resource=Resource.COAL.value,
            price=50,
            size=100,
            tick=1,
            timestamp=datetime.now(),
        ),
        "2": Order(
            pk="2",
            game_id="1",
            player_id="2",
            order_side=OrderSide.BUY.value,
            order_status=OrderStatus.ACTIVE.value,
            resource=Resource.OIL.value,
            price=50,
            size=100,
            tick=1,
            timestamp=datetime.now(),
        ),
    }

    tick_data = TickData(
        game=sample_game,
        players=sample_players,
        pending_orders=sample_pending_orders,
        user_cancelled_orders=sample_user_cancelled_orders,
        dataset_row=sample_dataset_row,
        markets=[],
        bots="",
        updated_orders=sample_update_orders,
        energy_market=sample_energy_market,
    )

    ticker.pipe = MagicMock()
    ticker.save_tick_data(tick_data)

    assert mock_player_save.call_count == 2
    assert mock_order_save.call_count == 2


def test_save_electricity_orders(sample_game, sample_players):
    players = sample_players
    game = sample_game
    energy_sold = {"1": 100, "2": 200}
    with patch("model.Trade.save") as mock_trade_create:
        ticker = Ticker()

        ticker.pipe = MagicMock()
        ticker.save_electricity_orders(
            players=players, game=game, energy_sold=energy_sold, tick=1
        )

        # Created two new energy orders
        assert mock_trade_create.call_count == 2


def test_save_market_data(ticker: Ticker, sample_game, tick_data):
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

    with patch("model.Market.save") as mock_save:
        ticker.pipe = MagicMock()
        ticker.save_market_data(tick_data)

        assert mock_save.call_count == len(Resource) + 1

        # Teze se testira s cim se pozivalo jer su u pozivima objekti
        # mock_save.assert_has_calls(expected_calls, any_order=True)
