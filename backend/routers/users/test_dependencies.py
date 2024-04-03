from fastapi import HTTPException
import pytest
from .dependencies import team_dep, game_dep, check_game_active_dep, player_dep, start_end_tick_dep
from model import Team, Game, Player
from unittest.mock import patch
from datetime import datetime, timedelta
from config import config


@pytest.mark.asyncio
async def test_team_dep():
    # not supplied
    try:

        await team_dep(None)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 403
        assert e.detail == "Missing team_secret"

    # exception raised in get
    with patch("model.Team.get") as mock:

        mock.side_effect = Exception()
        try:
            await team_dep()
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "Invalid team_secret"

    # valid team
    with patch("model.Team.get") as mock:
        t = Team(
            team_id=1, team_secret="secret", team_name="name")
        mock.return_value = t

        assert await team_dep() == t


@pytest.mark.asyncio
async def test_game_dep():
    # exception raised in get
    with patch("model.Game.get") as mock:
        mock.side_effect = Exception()
        try:
            await game_dep(1)
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "Invalid game_id"

    # valid game
    with patch("model.Game.get") as mock:
        g = Game(
            game_id=1, game_name="name", start_time=datetime.now(), is_finished=False,
            is_contest=False, dataset_id=1, current_tick=0, tick_time=1000, total_ticks=10)
        mock.return_value = g

        assert await game_dep(1) == g


@pytest.mark.asyncio
async def test_check_game_active_dep():
    # game is finished
    with patch("model.Game.get") as mock:
        g = Game(
            game_id=1, game_name="name", start_time=datetime.now(), is_finished=True,
            is_contest=False, dataset_id=1, current_tick=0, tick_time=1000, total_ticks=10)
        mock.return_value = g
        try:
            await check_game_active_dep(g)
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "Game is already finished"

    # game has not started yet
    with patch("model.Game.get") as mock:
        g = Game(
            game_id=1, game_name="name", start_time=datetime.now() + timedelta(days=1), is_finished=False,
            is_contest=False, dataset_id=1, current_tick=0, tick_time=1000, total_ticks=10)
        mock.return_value = g
        try:
            await check_game_active_dep(g)
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "Game has not started yet"

    # valid game
    with patch("model.Game.get") as mock:
        g = Game(
            game_id=1, game_name="name", start_time=datetime.now(), is_finished=False,
            is_contest=False, dataset_id=1, current_tick=1, tick_time=1000, total_ticks=10)
        mock.return_value = g
        assert await check_game_active_dep(g) is None


@pytest.mark.asyncio
async def test_player_dep():
    g = Game(
        game_id=1, game_name="name", start_time=datetime.now(), is_finished=False,
        is_contest=False, dataset_id=1, current_tick=0, tick_time=1000, total_ticks=10)
    # exception raised in get
    with patch("model.Player.get") as mock:
        mock.side_effect = Exception()
        try:
            await player_dep(1)
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "Invalid player_id"

    # player doesn't belong to team
    with patch("model.Player.get") as mock:
        p = Player(
            player_id=1, game_id=1, team_id=1, is_active=True, player_name="name")
        mock.return_value = p
        try:
            await player_dep(1, game=g, team=Team(team_id=2, team_name="team", team_secret="aaaaa"))
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 403
            assert e.detail == "This player doesn't belong to your team"

    # player is in another game
    with patch("model.Player.get") as mock:
        p = Player(
            player_id=1, game_id=2, team_id=1, is_active=True, player_name="name")
        mock.return_value = p
        try:
            await player_dep(1, game=g, team=Team(team_id=1, team_name="team", team_secret="aaaaa"))
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "This player is in game 2"

    # player is inactive
    with patch("model.Player.get") as mock:
        p = Player(
            player_id=1, game_id=1, team_id=1, is_active=False, player_name="name")
        mock.return_value = p
        try:
            await player_dep(1, game=g, team=Team(team_id=1, team_name="team", team_secret="aaaaa"))
            assert False  # pragma: no cover
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "This player is inactive or already has been deleted"

    # valid player
    with patch("model.Player.get") as mock:
        p = Player(
            player_id=1, game_id=1, team_id=1, is_active=True, player_name="name")
        mock.return_value = p
        assert await player_dep(1, game=g, team=Team(team_id=1, team_name="team", team_secret="aaaaa")) == p


@pytest.mark.asyncio
async def test_start_end_tick_dep():
    # game just started tests:

    g = Game(
        game_id=1, game_name="name", start_time=datetime.now(), is_finished=False,
        is_contest=False, dataset_id=1, current_tick=0, tick_time=1000, total_ticks=10)

    try:
        await start_end_tick_dep(g, None, None)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Game just started (it is tick=0), no data to return"

    try:
        await start_end_tick_dep(g, None, 10)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Game just started (it is tick=0), no data to return"

    try:
        await start_end_tick_dep(g, 10, None)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Game just started (it is tick=0), no data to return"

    # game running tests:

    g = Game(
        game_id=1, game_name="name", start_time=datetime.now(), is_finished=False,
        is_contest=False, dataset_id=1, current_tick=5, tick_time=1000, total_ticks=10)

    start, end = await start_end_tick_dep(g, 0, 4)
    assert start == 0
    assert end == 4

    start, end = await start_end_tick_dep(g, None, None)
    assert start == 4
    assert end == 4

    start, end = await start_end_tick_dep(g, None, 3)
    assert start == 3
    assert end == 3

    start, end = await start_end_tick_dep(g, 3, None)
    assert start == 3
    assert end == 3

    start, end = await start_end_tick_dep(g, -1, None)
    assert start == 4
    assert end == 4

    start, end = await start_end_tick_dep(g, None, -1)
    assert start == 4
    assert end == 4

    start, end = await start_end_tick_dep(g, -2, -2)
    assert start == 3
    assert end == 3

    start, end = await start_end_tick_dep(g, -100, -100)
    assert start == 0
    assert end == 0

    start, end = await start_end_tick_dep(g, -100, None)
    assert start == 0
    assert end == 0

    start, end = await start_end_tick_dep(g, None, -100)
    assert start == 0
    assert end == 0

    try:
        await start_end_tick_dep(g, 5, None)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Start tick must be less than current tick (current_tick=5)"

    try:
        await start_end_tick_dep(g, 5, 1000)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "Start tick must be less than current tick (current_tick=5)"

    try:
        await start_end_tick_dep(g, 4, -3)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "End tick must be greater than start tick"

    try:
        await start_end_tick_dep(g, 1, 5)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "End tick must be less than current tick (current_tick=5)"

    g.current_tick = 500
    g.total_ticks = 1000

    max_ticks_in_request = config["dataset"]["max_ticks_in_request"]

    try:
        await start_end_tick_dep(g, 0, max_ticks_in_request + 1)
        assert False  # pragma: no cover
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == f"Cannot request more than {max_ticks_in_request} ticks at once"
