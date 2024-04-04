from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

from algotrade_api import AlgotradeApi


url = "localhost:8000"

team_secret = "3EUX6JBT"
game_id = 2
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

        print(f"Player COAL: {player['coal']}")
        print(f"Player MONEY: {player['money']}")

        # list available market orders
        r = api.get_orders()
        assert r.status_code == 200, r.text

        orders = r.json()["COAL"]

        # filter for only sell orders
        orders = [order for order in orders if order["order_side"] == "SELL"]

        # find the cheapest order
        cheapest = sorted(orders, key=lambda x: x["price"])[0]
        cheapest_price = cheapest["price"]
        size = cheapest["size"]

        print("buying resources")
        print(f"Cheapest price: {cheapest_price}, size: {size}")

        r = api.create_order("COAL", cheapest_price + 1000,
                             1, "BUY", expiration_length=10)
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
