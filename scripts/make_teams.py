import requests
from datetime import datetime, timedelta

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
     "dataset_name": "df_2431_2011-11-06 03:30:00_2012-02-15 09:30:00.csv",
     "start_time": (datetime.now() + timedelta(minutes=1)).isoformat(),
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


def make_game(game):
    r = requests.post(f"http://{URL}/admin/game/create",
                      json=game, params={"admin_secret": ADMIN_SECRET})
    assert r.status_code == 200, r.text


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
