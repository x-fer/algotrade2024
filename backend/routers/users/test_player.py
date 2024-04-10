from fastapi import FastAPI
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from model import Player
from model.player import Networth
from .player import router
import pytest
from fixtures.fixtures import *
from routers.users.dependencies import game_dep, team_dep, check_game_active_dep, player_dep

from routers.users.fixtures import mock_check_game_active_dep, override_game_dep, override_team_dep, mock_player_dep, set_mock_find

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


def test_player_list():
    # mora vratiti samo is_active=True
    with patch("routers.users.player.Player.find") as mock_list:
        set_mock_find(mock_list, 'all', [
            Player(pk="1", game_id="1", team_id="1",
                   player_name="player_1", money=100),
        ])

        response = client.get("/game/1/player/list?team_secret=secret")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["player_id"] == "1"


def test_player_create_first():
    with patch("routers.users.player.Player.find") as mock_count:
        set_mock_find(mock_count, 'count', 0)

        response = client.post("/game/1/player/create?team_secret=secret")

    assert response.status_code == 200
    assert "player_id" in response.json()


def test_player_create_second():
    with patch("routers.users.player.Player.find") as mock_count:
        set_mock_find(mock_count, 'count', 1)

        response = client.post("/game/1/player/create?team_secret=secret")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only one player per team can be created in contest mode"}


def test_player_create_no_body():
    with patch("routers.users.player.Player.find") as mock_count:
        set_mock_find(mock_count, 'count', 0)

        response = client.post("/game/1/player/create?team_secret=secret")

        assert response.status_code == 200
        assert response.json()["player_name"] == "team_1_0"

def test_player_create_no_name():
    with patch("routers.users.player.Player.find") as mock_count:
        set_mock_find(mock_count, 'count', 0)
        response = client.post("/game/1/player/create?team_secret=secret", json={})

        assert response.status_code == 200
        assert response.json()["player_name"] == "team_1_0"

def test_player_create_player_name():
    with patch("routers.users.player.Player.find") as mock_count:
        set_mock_find(mock_count, 'count', 0)
        response = client.post(
            "/game/1/player/create?team_secret=secret", json={"player_name": "player_1"})

        assert response.status_code == 200
        assert response.json()["player_name"] == "player_1"


def test_player_get():
    # oponasamo pravi depencency, ali brojimo koliko puta je pozvan
    mock_check_game_active_dep.call_count = 0

    with patch("routers.users.player.Player.get") as mock_get:
        mock_get.return_value = Player(
            pk="1", game_id="1", team_id="1",
            player_name="player_1", money=100)

        response = client.get("/game/1/player/1?team_secret=secret")

    # Za dohvatiti igraca, vise nemamo dependency da je igra upaljena
    assert mock_check_game_active_dep.call_count == 0

    assert response.status_code == 200
    assert response.json()["player_id"] == "1"
    assert response.json()["player_name"] == "player_1"
    assert response.json()["money"] == 100


def test_player_delete_non_contest_mode():
    mock_player_dep.call_count = 0
    override_game_dep.contest = int(False)

    with patch("model.Player.update") as mock_update, \
        patch("model.Player.get") as mock_get, patch("model.Player.lock"):
        # Player se dohvaca dvaput jer je jednom u transactionu
        mock_get.return_value = Player(pk="1", game_id="1", team_id="1", player_name="player_1", money=100)
        response = client.get("/game/1/player/1/delete?team_secret=secret")

    assert response.status_code == 200, response.json()
    assert mock_player_dep.call_count == 1
    assert response.status_code == 200
    assert mock_update.call_count == 1

def test_player_delete_contest_mode():
    mock_player_dep.call_count = 0
    override_game_dep.contest = int(True)

    with patch("routers.users.player.Player.update") as mock_update:
        response = client.get("/game/1/player/1/delete?team_secret=secret")
        assert mock_update.call_count == 0

    assert mock_player_dep.call_count == 1
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Players cannot be deleted in contest mode"}


def test_player_net_worth():
    sample_return = Networth()

    with patch("routers.users.player.Player.get_networth") as mock_get_networth:
        mock_get_networth.return_value = sample_return
        response = client.get("/game/1/player/1/networth?team_secret=secret")

        assert mock_get_networth.call_count == 1

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["money"] == 0
    assert "resources" in response.json()
    assert "resources_value" in response.json()
    assert "power_plants_owned" in response.json()
    assert "power_plants_value" in response.json()
