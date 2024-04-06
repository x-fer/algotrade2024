from multiprocessing import Pool
import random
from time import sleep
import requests
from pprint import pprint
from datetime import datetime, timedelta

from algotrade_api import AlgotradeApi, Resource


url = "localhost:3000"

team_secret = "gogi"
game_id = 1

api = AlgotradeApi(url, team_secret, game_id)

resource = Resource.coal

def to_datetime(date: str):
    return datetime.fromisoformat(date.replace('Z', '+00:00'))

def tick():
    game = api.get_game().json()

    next_tick = to_datetime(game["next_tick_time"])
    current_tick = to_datetime(game["current_time"])

    diff = next_tick - current_tick
    diff = diff.total_seconds()
    print(diff)
    sleep(max(0.01, diff + 0.1))


def play():
    while True:
        tick()
        
        r = api.get_player()
        assert r.status_code == 200, r.text
        player = r.json()

        # we get the plant prices if we want to buy a plant
        r = api.get_plant_prices()
        assert r.status_code == 200, r.text
        plant_prices = r.json()

        # we set the energy price to sell our energy, if it's higher than the market, it won't sell
        energy_price = random.randint(400, 500)
        r = api.set_energy_price(energy_price)
        assert r.status_code == 200, r.text

        # we turn on as many plants as we can burn coal this turn
        player_power_plants = player[f"{resource.value.lower()}_plants_owned"]
        t = api.turn_on(resource.value, player_power_plants)
        assert r.status_code == 200, r.text

        print(f"Player {resource.name}: {player[resource.value.lower()]}")
        print(f"Player MONEY: {player['money']}")
        print(f"Player power plant: {player_power_plants}")

        # if we can buy a plant we buy it (20000 is some slack to get resources)
        if plant_prices[resource.value]["next_price"] + 2_000_000 <= player["money"]:
            print(f"buying power {resource.name} plant")
            r = api.buy_plant(resource.value)
            assert r.status_code == 200, r.text
            continue

        # if we can't buy a plant we buy resources
        if player[resource.value.lower()] < 30:
            # list available market orders
            r = api.get_orders(restriction="best")
            assert r.status_code == 200, r.text
            
            orders = r.json()[resource.value]

            # filter for only sell orders
            orders = [order for order in orders if order["order_side"] == "SELL"]

            # find the cheapest order
            cheapest = sorted(orders, key=lambda x: x["price"])[0]
            cheapest_price = cheapest["price"]
            size = cheapest["size"]

            # size is min what can be bought, we don't want to buy more than 50, and we can't buy more than we can afford
            size = min(size, 50 - player[resource.value.lower()],
                       int(player["money"] // cheapest_price))

            if size == 0:
                continue

            print("buying resources")
            print(f"Cheapest price: {cheapest_price}, size: {size}")

            r = api.create_order(resource.value, cheapest_price + 10, size, "BUY", expiration_length=10)
            assert r.status_code == 200, r.text

            continue


def run(x):
    # each game, we must create a new player
    # in contest mode, we can make only one
    # r = api.create_player("bot1")
    # assert r.status_code == 200, r.text

    # print("Player created")
    # pprint(r.json())

    # player_id = r.json()["player_id"]

    api.set_player_id(1)
    play()


def main():
    # with Pool(25) as p:
    #     p.map(run, range(25))

    run(1)


if __name__ == "__main__":
    main()
