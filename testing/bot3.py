from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

from algotrade_api import AlgotradeApi


url = "localhost:3000"

team_secret = "gogi"
game_id = 1
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

        print(f"Player COAL: {player['resources']['coal']}")
        print(f"Player MONEY: {player['money']}")

        # list available market orders
        r = api.get_orders(restriction="best")
        assert r.status_code == 200, r.text
        print(r.json())

        orders = r.json()["coal"]

        best_order = orders["SELL"][0]
        print(best_order)
        best_price = best_order['price']
        best_size = best_order["size"]

        print("buying resources")
        print(f"Cheapest price: {best_price}, size: {best_size}")

        r = api.create_order("coal", best_price + 1000, 1, "BUY", expiration_length=10)
        assert r.status_code == 200, r.text

        continue


def run(x):
    games = api.get_games().json()
    print(games)
    game = games[0]

    api.set_game_id(game["game_id"])

    print("Creating player")
    response = api.create_player()
    print(response.json())
    # pprint(response.json())

    player_id = response.json()["player_id"]
    api.set_player_id(player_id)

    print(api.get_players().json())

    play()


def main():

    # with Pool(25) as p:
    #     p.map(run, range(25))

    run(1)


if __name__ == "__main__":
    main()
