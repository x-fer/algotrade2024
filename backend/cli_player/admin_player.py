from datetime import datetime, timedelta
from pprint import pprint
import requests

URL = "localhost:8000"
admin_secret = "mojkljuc"
game_id = "1"


def set_admin_secret():
    global admin_secret

    new_admin_secret = input("Enter new admin secret: ")

    if new_admin_secret:
        admin_secret = new_admin_secret
        print(f"Admin secret set to: {admin_secret}")
    else:
        print("Admin secret not set")


def set_game_id():
    global game_id

    new_game_id = input("Enter new game id: ")

    if new_game_id:
        game_id = new_game_id
        print(f"Game id set to: {game_id}")
    else:
        print("Game id not set")


def migrate():
    response = requests.get(
        f"http://{URL}/admin/migrate", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def list_datasets():
    response = requests.get(
        f"http://{URL}/admin/dataset/list", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def list_bots():
    response = requests.get(
        f"http://{URL}/admin/bot/list", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def create_game():
    game_name = input("Enter game name: ")
    contest = input("Is contest? (true/false): ")

    if contest not in ["true", "false"]:
        print("Invalid input")
        return
    contest = contest == "true"

    dataset_id = input("Enter dataset id: ")

    start_time = input(
        "Enter start time (YYYY-MM-DDTHH:MM:SS) or now_Xmin to start X mins from now: ")
    if start_time.startswith("now_"):
        start_time = int(start_time[4:-3])
        start_time = datetime.now() + timedelta(minutes=start_time)
    else:
        start_time = datetime.fromisoformat(start_time)

    total_ticks = int(input("Enter total ticks: "))
    tick_time = int(input("Enter tick time (ms): "))

    response = requests.post(
        f"http://{URL}/admin/game/create",
        params={"admin_secret": admin_secret},
        json={
            "game_name": game_name,
            "contest": contest,
            "dataset_id": dataset_id,
            "start_time": start_time.isoformat(),
            "total_ticks": total_ticks,
            "tick_time": tick_time
        }
    )

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def list_games():
    response = requests.get(
        f"http://{URL}/admin/game/list", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
        pprint(response.json())
    else:
        pprint(response.json())


def list_players():
    response = requests.get(
        f"http://{URL}/admin/game/{game_id}/player/list", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def delete_game():
    global game_id

    response = requests.get(
        f"http://{URL}/admin/game/{game_id}/delete", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def edit_game():

    game_name = input("Enter game name: ")
    contest = input("Is contest? (true/false): ")

    if contest not in ["true", "false"]:
        print("Invalid input")
        return

    contest = contest == "true"

    bots = input("Enter bots: ")
    dataset_id = input("Enter dataset id: ")

    start_time = input(
        "Enter start time (YYYY-MM-DDTHH:MM:SS) or now_Xmin to start X mins from now: ")

    if start_time.startswith("now_"):
        start_time = int(start_time[4:-3])
        start_time = datetime.now() + timedelta(minutes=start_time)
    else:
        start_time = datetime.fromisoformat(start_time)

    total_ticks = int(input("Enter total ticks: "))
    tick_time = int(input("Enter tick time (ms): "))

    body = {}

    for key, value in [
        ("game_name", game_name),
        ("contest", contest),
        ("bots", bots),
        ("dataset_id", dataset_id),
        ("start_time", start_time.isoformat()),
        ("total_ticks", total_ticks),
        ("tick_time", tick_time)
    ]:
        if value:
            body[key] = value

    response = requests.post(
        f"http://{URL}/admin/game/{game_id}/edit",
        params={"admin_secret": admin_secret},
        json=body
    )

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def create_team():
    team_name = input("Enter team name: ")

    response = requests.post(
        f"http://{URL}/admin/team/create",
        params={"admin_secret": admin_secret},
        json={"team_name": team_name}
    )

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def list_teams():
    response = requests.get(
        f"http://{URL}/admin/team/list", params={"admin_secret": admin_secret})

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def delete_team():
    team_id = input("Enter team id: ")

    response = requests.get(
        f"http://{URL}/admin/team/{team_id}/delete",
        params={"admin_secret": admin_secret}
    )

    if response.status_code != 200:
        print("Error " + response.status_code)
    pprint(response.json())


def main():
    global admin_secret

    while True:
        print()
        print("Choose action:")
        print(f"1. Set Admin Secret, current: {admin_secret}")
        print(f"2. Set Game ID, current: {game_id}")
        print(f"3. Migrate database")
        print(f"4. List datasets")
        print(f"5. List bots")
        print(f"6. Create game")
        print(f"7. List games")
        print(f"8. List players")
        print(f"9. Delete game")
        print(f"10. Edit game")
        print(f"11. Create team")
        print(f"12. List teams")
        print(f"13. Delete team")
        print(f"14. Exit")
        print()

        action = input(">")

        case = {
            "1": lambda: set_admin_secret(),
            "2": lambda: set_game_id(),
            "3": lambda: migrate(),
            "4": lambda: list_datasets(),
            "5": lambda: list_bots(),
            "6": lambda: create_game(),
            "7": lambda: list_games(),
            "8": lambda: list_players(),
            "9": lambda: delete_game(),
            "10": lambda: edit_game(),
            "11": lambda: create_team(),
            "12": lambda: list_teams(),
            "13": lambda: delete_team(),
            "14": lambda: exit(0)
        }

        try:
            case[action]()
            print()
        except KeyError:
            print("Invalid action")


if __name__ == "__main__":
    main()
