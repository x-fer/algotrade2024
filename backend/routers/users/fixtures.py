from datetime import datetime
from fastapi import Query, Depends
from model import Game, Team, Player
from routers.users.dependencies import game_dep, team_dep, check_game_active_dep, player_dep, start_end_tick_dep


def override_game_dep(game_id: int) -> Game:
    assert game_id == 1
    if not hasattr(override_game_dep, "contest"):
        override_game_dep.contest = True
    if not hasattr(override_game_dep, "tick"):
        override_game_dep.tick = 0
    return Game(game_id=1, game_name="game_1", is_active=True, is_contest=override_game_dep.contest,
                dataset_id=1, start_time=datetime.now(), total_ticks=1000, tick_time=1000, current_tick=override_game_dep.tick)


def override_team_dep(team_secret: str = Query(description="Team secret", default=None)):
    assert team_secret == "secret"
    return Team(team_id=1, team_name="team_1", game_id=1, team_secret="secret")


def mock_check_game_active_dep(game: Game = Depends(game_dep)):
    mock_check_game_active_dep.call_count += 1
    return check_game_active_dep(game)


def mock_player_dep(game: Game = Depends(game_dep)):
    if not hasattr(mock_player_dep, "call_count"):
        mock_player_dep.call_count = 0
    mock_player_dep.call_count += 1
    return Player(player_id=1, game_id=1, team_id=1, player_name="player_1", money=100)


def mock_start_end_tick_dep(game: Game = Depends(game_dep),
                                  start_tick: int = Query(default=None),
                                  end_tick: int = Query(default=None)):
    if not hasattr(mock_start_end_tick_dep, "call_count"):
        mock_start_end_tick_dep.call_count = 0
    mock_start_end_tick_dep.call_count += 1
    return start_end_tick_dep(game, start_tick, end_tick)
