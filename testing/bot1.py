from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

from algotrade_api import AlgotradeApi


url = "localhost:8000"

team_secret = "GUWAPRGW"
game_id = "01HV3TAMMQNK1TSF9RYP9W8VF5"
player_id = -1  # we will get this later

api = AlgotradeApi(url, team_secret, game_id, player_id)


def play():
    while True:
        # tick time is 1 second
        sleep(1)

        # we get our player stats
        r = api.get_player()
        assert r.status_code == 200, r.text
        player = r.json()

        # we get the plant prices if we want to buy a plant
        r = api.get_plant_prices()
        assert r.status_code == 200, r.text
        plant_prices = r.json()
        pprint(plant_prices)

        # we set the energy price to sell our energy, if it's higher than the market, it won't sell
        energy_price = random.randint(400, 500)
        r = api.set_energy_price(energy_price)
        assert r.status_code == 200, r.text

        # we turn on as many plants as we can burn coal this turn
        r = api.turn_on(
            "coal", player["power_plants_owned"]["coal"])
        assert r.status_code == 200, r.text

        print(f"Player COAL: {player['resources']['coal']}")
        print(f"Player MONEY: {player['money']}")

        # if we can buy a plant we buy it (20000 is some slack to get resources)
        if plant_prices["buy_price"]["COAL"] + 2_000_000 <= player["money"]:
            r = api.buy_plant("coal")
            assert r.status_code == 200, r.text
            continue

        # if we can't buy a plant we buy resources
        if player["resources"]["coal"] < 30:
            # list available market orders
            r = api.get_orders()
            assert r.status_code == 200, r.text

            orders = r.json()["coal"]
            pprint(orders)

            # filter for only sell orders
            orders = [order for order in orders["sell"]]

            # find the cheapest order
            cheapest = sorted(orders, key=lambda x: x["price"])[0]
            cheapest_price = cheapest["price"]
            size = cheapest["size"]

            # size is min what can be bought, we don't want to buy more than 50, and we can't buy more than we can afford
            size = min(size, 50 - player["resources"]["coal"],
                       int(player["money"] // cheapest_price))

            if size == 0:
                continue

            print("buying resources")
            print(f"Cheapest price: {cheapest_price}, size: {size}")

            r = api.create_order("coal", cheapest_price + 10,
                                 size, "buy", expiration_length=10)
            assert r.status_code == 200, r.text

            continue


def run(x):
    # each game, we must create a new player
    # in contest mode, we can make only one
    r = api.create_player("bot1")
    assert r.status_code == 200, r.text

    print("Player created")
    pprint(r.json())

    player_id = r.json()["player_id"]

    api.set_player_id(player_id)
    play()


def main():

    # with Pool(25) as p:
    #     p.map(run, range(25))

    run(1)


if __name__ == "__main__":
    main()
