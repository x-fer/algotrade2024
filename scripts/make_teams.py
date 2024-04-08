import requests
from datetime import datetime, timedelta
from pprint import pprint

URL = "localhost:8000"
ADMIN_SECRET = "mojkljuc"

teams = [
    {"team_name": "maja"},
    {"team_name": "goran"},
    {"team_name": "zvone"},
    {"team_name": "kruno"}
]


games = [
    {"game_name": "game1",
     "contest": False,
     "dataset_name": "df_2431 Nov 6 2011 to Feb 15 2012.csv",
     "start_time": (datetime.now() + timedelta(seconds=5)).isoformat(),
     "total_ticks": 1000,
     "tick_time": 1000},
]


def get_datasets():
    r = requests.get(f"http://{URL}/admin/dataset/list",
                     params={"admin_secret": ADMIN_SECRET})
    assert r.status_code == 200, r.text
    return r.json()


def make_team(team):
    r = requests.post(f"http://{URL}/admin/team/create",
                      json=team, params={"admin_secret": ADMIN_SECRET})
    assert r.status_code == 200, r.text

    print(f"Team {team['team_name']} created")
    pprint(r.json())


def make_game(game):
    r = requests.post(f"http://{URL}/admin/game/create",
                      json=game, params={"admin_secret": ADMIN_SECRET})
    assert r.status_code == 200, r.text


def list_games():
    r = requests.get(f"http://{URL}/admin/game/list",
                     params={"admin_secret": ADMIN_SECRET})
    assert r.status_code == 200, r.text
    print("Games:")
    pprint(r.json())


if __name__ == "__main__":
    datasets = get_datasets()

    for game in games:
        assert any(
            dataset["dataset_name"] == game["dataset_name"] for dataset in datasets
        ), f"Dataset {game['dataset_name']} not found"

    for team in teams:
        make_team(team)

    for game in games:
        game["dataset_id"] = [
            dataset["dataset_id"] for dataset in datasets
            if dataset["dataset_name"] == game["dataset_name"]
        ][0]
        del game["dataset_name"]

        make_game(game)

    list_games()
