from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

import algotrade_api
from algotrade_api import AlgotradeApi


url = "localhost:3000"

team_secret = "1IM56G5I"
game_id = "01HV2CQJ19BF2T1Z8Q8MZ7W319"
player_id = -1  # we will get this later

api = AlgotradeApi(url, team_secret, game_id, player_id)


def play():
    while True:
        # tick time is 1 second
        sleep(0.9)

        # we get our player stats
        r = api.get_player()
        assert r.status_code == 200, r.text
        player = r.json()

        # print(f"Player COAL: {player['resources']['coal']}")
        print(f"{player['player_id']} money: {player['money']}")
        # print(player['resources'])

        # list available market orders
        r = api.get_orders(restriction="best")
        assert r.status_code == 200, r.text
        # print(r.json())
        rjson = r.json()

        for resource in algotrade_api.Resource:
            try:
                orders = rjson[resource.value]
                best_order = orders["sell"][0]
                # print(best_order)
                best_price = best_order['price']
                best_size = best_order["size"]
            except:
                continue

            print(
                f"{player['player_id']} Buying {resource.value} price: {best_price}, size: {best_size}")

            r = api.create_order("coal", best_price + 1000,
                                 1, "buy", expiration_length=10)
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

    with Pool(5) as p:
        p.map(run, range(5))

    # run(1)


if __name__ == "__main__":
    main()
