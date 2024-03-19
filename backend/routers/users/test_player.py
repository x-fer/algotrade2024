from fastapi import FastAPI
from unittest.mock import patch
from fastapi.testclient import TestClient

from model import Player
from .player import router
import pytest
from fixtures.fixtures import *
from routers.users.dependencies import game_dep, team_dep, check_game_active_dep, player_dep

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
    with patch("db.db.database.transaction") as mock_transaction:
        yield mock_transaction


def test_player_list():
    # mora vratiti samo is_active=True
    with patch("routers.users.player.Player.list") as mock_list:
        mock_list.return_value = [
            Player(player_id=1, game_id=1, team_id=1,
                   player_name="player_1", money=100),
        ]

        response = client.get(f"/game/1/player/list?team_secret=secret")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["player_id"] == 1


def test_player_create_first():
    with patch("routers.users.player.Player.create") as mock_create, \
            patch("routers.users.player.Player.count") as mock_count:
        mock_create.return_value = 1
        mock_count.return_value = 0

        response = client.post(f"/game/1/player/create?team_secret=secret")

    assert response.status_code == 200
    assert response.json()["player_id"] == 1


def test_player_create_second():
    with patch("routers.users.player.Player.create") as mock_create, \
            patch("routers.users.player.Player.count") as mock_count:
        mock_create.return_value = 1
        mock_count.return_value = 1

        response = client.post(f"/game/1/player/create?team_secret=secret")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only one player per team can be created in contest mode"}


def test_player_create_possible_bodies():
    # player_create: PlayerCreate | None | dict = None
    with patch("routers.users.player.Player.create") as mock_create, \
            patch("routers.users.player.Player.count") as mock_count:
        mock_create.return_value = 1
        mock_count.return_value = 0

        # no body
        response = client.post(f"/game/1/player/create?team_secret=secret")

        assert response.status_code == 200
        assert mock_create.call_args.kwargs["player_name"] == "team_1_0"

        # empty dict
        response = client.post(
            f"/game/1/player/create?team_secret=secret", json={})

        assert response.status_code == 200
        assert mock_create.call_args.kwargs["player_name"] == "team_1_0"

        # player_name in body
        response = client.post(
            f"/game/1/player/create?team_secret=secret", json={"player_name": "player_1"})

        assert response.status_code == 200
        assert mock_create.call_args.kwargs["player_name"] == "player_1"


def test_player_get():

    # oponasamo pravi depencency, ali brojimo koliko puta je pozvan
    mock_check_game_active_dep.call_count = 0

    with patch("routers.users.player.Player.get") as mock_get:

        mock_get.return_value = Player(player_id=1, game_id=1, team_id=1,
                                       player_name="player_1", money=100)

        response = client.get(f"/game/1/player/1?team_secret=secret")

    assert mock_check_game_active_dep.call_count == 1

    assert response.status_code == 200
    assert response.json()["player_id"] == 1
    assert response.json()["player_name"] == "player_1"
    assert response.json()["money"] == 100


def test_player_delete():
    # non contest mode

    mock_player_dep.call_count = 0
    override_game_dep.contest = False

    with patch("routers.users.player.Player.update") as mock_update:
        response = client.get(f"/game/1/player/1/delete?team_secret=secret")
        assert mock_update.call_count == 1

    assert mock_player_dep.call_count == 1
    assert response.status_code == 200

    # contest mode

    mock_player_dep.call_count = 0
    override_game_dep.contest = True

    with patch("routers.users.player.Player.update") as mock_update:
        response = client.get(f"/game/1/player/1/delete?team_secret=secret")
        assert mock_update.call_count == 0

    assert mock_player_dep.call_count == 1
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Players cannot be deleted in contest mode"}


def test_player_net_worth():
    sample_return = {
        "plants_owned": {"coal": {"owned": 1, "value_if_sold": 100}},
        "money": 100,
        "resources": {"coal": {"coal": 100}},
        "total": 200
    }

    with patch("routers.users.player.Player.get_networth") as mock_get_networth:
        mock_get_networth.return_value = sample_return
        response = client.get(f"/game/1/player/1/networth?team_secret=secret")

        assert mock_get_networth.call_count == 1

    assert response.status_code == 200
    assert response.json() == sample_return
