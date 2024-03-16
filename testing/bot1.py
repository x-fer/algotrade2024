from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

url = "http://localhost:8000"


def create_team():
    r = requests.post(url + "/admin/team/create",
                      params={"admin_secret": "mojkljuc"},
                      json={"team_name": "test_team", "team_secret": "mojkljuc"})

    assert r.status_code == 200

    r = requests.get(url + "/admin/team/list",
                     params={"admin_secret": "mojkljuc"})

    team_secret = [x["team_secret"]
                   for x in r.json() if x["team_name"] == "test_team"][0]

    return team_secret


def make_game():
    now = datetime.now() + timedelta(seconds=1)
    r = requests.post(url + "/admin/game/create",
                      params={"admin_secret": "mojkljuc"},
                      json={"game_name": "test_game", "contest": False, "dataset_id": "1", "total_ticks": 1800, "tick_time": 1000, "start_time": now.isoformat()})

    assert r.status_code == 200

    r = requests.get(url + "/admin/game/list",
                     params={"admin_secret": "mojkljuc"})

    game_id = [x["game_id"]
               for x in r.json() if x["game_name"] == "test_game"][0]

    return game_id


def create_player(game_id, team_secret):

    r = requests.post(url + f"/game/{game_id}/player/create",
                      params={"team_secret": team_secret},
                      json={"player_name": "test_player"})

    assert r.status_code == 200

    return r.json()["player_id"]


def get_player(game_id, player_id, team_secret):
    r = requests.get(url + f"/game/{game_id}/player/{player_id}",
                     params={"team_secret": team_secret})

    assert r.status_code == 200, r.text

    return r.json()


def get_plant_prices(game_id, player_id, team_secret):
    r = requests.get(url + f"/game/{game_id}/player/{player_id}/plant/list",
                     params={"team_secret": team_secret})

    assert r.status_code == 200, r.text

    return r.json()


def buy_plant(game_id, player_id, team_secret, plant_type):
    r = requests.post(url + f"/game/{game_id}/player/{player_id}/plant/buy",
                      params={"team_secret": team_secret},
                      json={"type": plant_type})

    assert r.status_code == 200, r.text


def buy_resources(game_id, player, team_secret, resource, amount):
    # /game/{game_id}/orders
    r = requests.get(url + f"/game/{game_id}/orders",
                     params={"team_secret": team_secret, "restrictions": "all"})

    # @router.post("/game/{game_id}/player/{player_id}/orders/create")

    print()
    pprint(r.json())

    coal_sell_orders = [x for x in r.json()[resource]
                        if x["order_side"] == "SELL"]

    if len(coal_sell_orders) == 0:
        print("No coal to buy")
        return

    cheapest = min([x for x in coal_sell_orders], key=lambda x: x["price"])

    can_buy = min(player["money"] // cheapest["price"],
                  amount, cheapest["size"])

    if can_buy > 0:
        r = requests.post(url + f"/game/{game_id}/player/{player['player_id']}/orders/create",
                          params={"team_secret": team_secret},
                          json={"resource": resource, "size": can_buy, "price": cheapest["price"], "side": "BUY", "expiration_length": 10})
        if r.status_code == 200:
            print(f"Placed order for {can_buy} {resource}")
        else:
            print(r.text)
    else:
        print("No resources to buy")

# class PowerOn(BaseModel):
#     type: PowerPlantType
#     number: int


# @router.post("/game/{game_id}/player/{player_id}/plant/on")

def turn_on(game_id, player_id, team_secret, plant_type, number):
    r = requests.post(url + f"/game/{game_id}/player/{player_id}/plant/on",
                      params={"team_secret": team_secret},
                      json={"type": plant_type, "number": number})

    assert r.status_code == 200, r.text


def set_energy_price(price, game_id, player_id, team_secret):
    r = requests.post(url + f"/game/{game_id}/player/{player_id}/energy/set_price",
                      params={"team_secret": team_secret},
                      json={"price": price})

    assert r.status_code == 200, r.text


def play(game_id, player_id, team_secret):
    while True:
        player = get_player(game_id, player_id, team_secret)
        plant_prices = get_plant_prices(game_id, player_id, team_secret)

        energy_price = random.randint(450, 500)
        set_energy_price(energy_price, game_id, player_id, team_secret)

        print(f"Player COAL: {player['coal']}")
        print(f"Player MONEY: {player['money']}")

        if plant_prices["COAL"]["next_price"] + 20000 <= player["money"]:
            buy_plant(game_id, player_id, team_secret, "COAL")
            continue

        if player["coal"] < 30:
            buy_resources(game_id, player, team_secret, "COAL", 30)
            sleep(1)

            continue

        turn_on(game_id, player_id, team_secret,
                "COAL", player["coal_plants_owned"])

        sleep(1)


def run(x):
    # migrate()
    team_secret = create_team()
    game_id = 4
    player_id = create_player(game_id, team_secret)

    play(game_id, player_id, team_secret)


def main():

    with Pool(25) as p:
        p.map(run, range(25))


if __name__ == "__main__":
    main()
