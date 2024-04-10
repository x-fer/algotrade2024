from datetime import datetime
from fastapi import FastAPI, Depends, Query
from unittest.mock import patch
from fastapi.testclient import TestClient

from model import Player
from .power_plant import router
import pytest
from fixtures.fixtures import *
from routers.users.dependencies import game_dep, team_dep, check_game_active_dep, player_dep

from routers.users.power_plant import PowerPlantData, PowerPlantTypeData
from routers.users.fixtures import mock_check_game_active_dep, override_game_dep, override_team_dep, mock_player_dep

app = FastAPI()
client = TestClient(app)

app.include_router(router)

app.dependency_overrides[check_game_active_dep] = mock_check_game_active_dep
app.dependency_overrides[game_dep] = override_game_dep
app.dependency_overrides[team_dep] = override_team_dep
app.dependency_overrides[player_dep] = mock_player_dep


@pytest.fixture(scope="session", autouse=True)
def mock_transaction():
    with patch("model.Player.lock") as mock_transaction:
        yield mock_transaction


def test_list_plants():
    mock_check_game_active_dep.call_count = 0

    response = client.get("/game/1/player/1/plant/list")

    assert response.status_code == 200
    assert "COAL" in response.json()
    assert mock_check_game_active_dep.call_count == 1


def test_buy_plant():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=0, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/buy", json={"type": "COAL"})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 200, response.text
        assert mock_update.call_count == 2
        assert mock_get.call_count == 1


def test_buy_plant_not_enough_money():
    mock_check_game_active_dep.call_count = 0
    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=0,
                                       coal_plants_owned=0, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/buy", json={"type": "COAL"})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 400, response.text


def test_buy_plant_sell_plant():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=1, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/sell", json={"type": "COAL"})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 200, response.text
        assert mock_update.call_count == 1
        assert mock_get.call_count == 1


def test_buy_plant_sell_plant_no_plant():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=0, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/sell", json={"type": "COAL"})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 400, response.text
        assert mock_update.call_count == 0
        assert mock_get.call_count == 1


def test_turn_on():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=1, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/on", json={"type": "COAL", "number": 1})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 200, response.text
        assert mock_update.call_count == 1
        assert mock_get.call_count == 1


def test_turn_on_no_plant():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=0, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/on", json={"type": "COAL", "number": 1})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 400, response.text
        assert mock_update.call_count == 0


def test_turn_on_negative():
    mock_check_game_active_dep.call_count = 0

    with patch("model.Player.get") as mock_get, \
            patch("model.Player.update") as mock_update:
        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=1e9,
                                       coal_plants_owned=10, oil_plants_owned=0, garbage_plants_owned=0, uranium_plants_owned=0)

        response = client.post(
            "/game/1/player/1/plant/on", json={"type": "COAL", "number": -1})

        assert mock_check_game_active_dep.call_count == 1
        assert response.status_code == 400, response.text
        assert mock_update.call_count == 0
