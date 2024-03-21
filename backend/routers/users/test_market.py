from fastapi import FastAPI
from unittest.mock import patch
from fastapi.testclient import TestClient

from model import Player, Market, Resource
from model.order_types import OrderStatus
from .market import router
import pytest
from fixtures.fixtures import *
from routers.users.dependencies import game_dep, team_dep, check_game_active_dep, player_dep, start_end_tick_dep
from datetime import datetime

from routers.users.fixtures import mock_check_game_active_dep, override_game_dep, override_team_dep, mock_player_dep, mock_start_end_tick_dep

app = FastAPI()
client = TestClient(app)

app.include_router(router)

app.dependency_overrides[check_game_active_dep] = mock_check_game_active_dep
app.dependency_overrides[game_dep] = override_game_dep
app.dependency_overrides[team_dep] = override_team_dep
app.dependency_overrides[player_dep] = mock_player_dep
app.dependency_overrides[start_end_tick_dep] = mock_start_end_tick_dep


@pytest.fixture(scope="session", autouse=True)
def mock_transaction():
    with patch("db.db.database.transaction") as mock_transaction:
        yield mock_transaction


def test_market_prices():
    mock_start_end_tick_dep.call_count = 0
    mock_check_game_active_dep.call_count = 0
    override_game_dep.tick = 4
    with patch("model.Market.list_by_game_id_where_tick") as mock_list:
        mock_list.return_value = [
            Market(game_id=1, tick=1, resource=Resource.coal, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
            Market(game_id=1, tick=2, resource=Resource.coal, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
            Market(game_id=1, tick=3, resource=Resource.coal, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
            Market(game_id=1, tick=1, resource=Resource.oil, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
            Market(game_id=1, tick=2, resource=Resource.oil, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
            Market(game_id=1, tick=3, resource=Resource.oil, low=10, high=20,
                   open=15, close=18, market=15, volume=100),
        ]

        response = client.get("/game/1/market/prices?start_tick=1&end_tick=3")
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert mock_start_end_tick_dep.call_count == 1
        assert len(response.json()["COAL"]) == 3
        assert len(response.json()["OIL"]) == 3


def test_energy_set_price_player():
    # OK
    mock_check_game_active_dep.call_count = 0
    mock_player_dep.call_count = 0
    override_game_dep.tick = 4

    with patch("model.Player.update") as mock_update:
        response = client.post(
            "/game/1/player/1/energy/set_price", json={"price": 10})
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert mock_player_dep.call_count == 1
        mock_update.assert_called_once_with(
            player_id=1,
            energy_price=10
        )

    # Price <= 0
    mock_check_game_active_dep.call_count = 1
    mock_player_dep.call_count = 0
    override_game_dep.tick = 4

    with patch("model.Player.update") as mock_update:
        response = client.post(
            "/game/1/player/1/energy/set_price", json={"price": -10})
        assert response.status_code == 400, response.text
        assert mock_check_game_active_dep.call_count == 2
        assert mock_player_dep.call_count == 1
        assert mock_update.call_count == 0


def test_order_list():

    with patch("model.Order.list") as mock_list, \
            patch("model.Order.list_bot_orders_by_game_id") as mock_bot_list, \
            patch("model.Order.list_best_orders_by_game_id") as mock_best_list:

        # return all orders
        mock_list.return_value = [
            Order(game_id=1, order_id=1, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.coal),
            Order(game_id=1, order_id=2, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.SELL, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.oil),
        ]

        # return bot orders (koristimo i za buy i za sell)
        mock_bot_list.return_value = [
            Order(game_id=1, order_id=3, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.coal),
            Order(game_id=1, order_id=4, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.SELL, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.oil),
        ]

        # return best orders (koristimo i za buy i za sell)
        mock_best_list.return_value = [
            Order(game_id=1, order_id=5, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.coal),
            Order(game_id=1, order_id=6, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.SELL, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.oil),
        ]

        mock_check_game_active_dep.call_count = 0
        override_game_dep.tick = 4

        # no argument, we get .list() as output
        response = client.get("/game/1/orders")
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert len(sum(response.json().values(), [])) == 2
        assert "COAL" in response.json()

        mock_check_game_active_dep.call_count = 0
        override_game_dep.tick = 4

        # bot orders
        response = client.get("/game/1/orders?restriction=bot")
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert len(sum(response.json().values(), [])) == 2
        assert "COAL" in response.json()
        assert len(response.json()["COAL"]) == 1
        assert len(response.json()["OIL"]) == 1

        mock_check_game_active_dep.call_count = 0
        override_game_dep.tick = 4

        # best orders
        response = client.get("/game/1/orders?restriction=best")
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert len(sum(response.json().values(), [])) == 4
        assert "COAL" in response.json()

        # cudno, ali jer ima sell + buy, a mi vratimo isto za oba
        assert len(response.json()["COAL"]) == 2
        assert len(response.json()["OIL"]) == 2


def test_order_list_player():
    with patch("model.Order.list") as mock_list:
        mock_list.return_value = [
            Order(game_id=1, order_id=1, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.coal),
            Order(game_id=1, order_id=2, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
            ), order_side=OrderSide.SELL, order_status=OrderStatus.PENDING, filled_size=0, expiration_tick=100, resource=Resource.oil),
        ]

        mock_check_game_active_dep.call_count = 0
        mock_player_dep.call_count = 0
        override_game_dep.tick = 4

        response = client.get("/game/1/player/1/orders")
        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert mock_player_dep.call_count == 1

        assert len(sum(response.json().values(), [])
                   ) == 4  # 2 active + 2 pending

        assert "COAL" in response.json()
        assert len(response.json()["COAL"]) == 2
        assert len(response.json()["OIL"]) == 2


def test_order_get_player():
    with patch("model.Order.get") as mock_get:
        mock_get.return_value = Order(game_id=1, order_id=1, player_id=1, price=10, size=10, tick=1, timestamp=datetime.now(
        ), order_side=OrderSide.BUY, order_status=OrderStatus.ACTIVE, filled_size=0, expiration_tick=100, resource=Resource.coal)

        mock_check_game_active_dep.call_count = 0
        mock_player_dep.call_count = 0
        override_game_dep.tick = 4

        response = client.get("/game/1/player/1/orders/1")

        assert response.status_code == 200, response.text
        assert mock_check_game_active_dep.call_count == 1
        assert mock_player_dep.call_count == 1
        assert response.json()["order_id"] == 1


@pytest.mark.asyncio
async def test_order_create_player():
    response = client.post("/game/1/player/1/orders/create", json={
        "resource": "COAL",
        "price": 10,
        "size": 10,
        "side": "BUY",
    })

    assert response.status_code == 400, response.text

    response = client.post("/game/1/player/1/orders/create", json={
        "resource": "COAL",
        "price": 10,
        "size": 10,
        "side": "BUY",
        "expiration_length": -10
    })

    assert response.status_code == 400, response.text

    response = client.post("/game/1/player/1/orders/create", json={
        "resource": "COAL",
        "price": 10,
        "size": 10,
        "side": "BUY",
        "expiration_tick": 0
    })

    assert response.status_code == 400, response.text
