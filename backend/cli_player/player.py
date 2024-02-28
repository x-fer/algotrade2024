from pprint import pprint
import requests

# GET
# /game/list
# Game List


# GET
# /game/{game_id}/dataset
# Dataset List

# Player
# You will be able to

# Create player in a game
# Get all created players in a game
# Get player info - player resources, money, power plants etc.


# GET
# /game/{game_id}/player/list
# Player List


# POST
# /game/{game_id}/player/create
# Player Create


# GET
# /game/{game_id}/player/{player_id}
# Player Get


# GET
# /game/{game_id}/player/{player_id}/delete
# Player Delete

# Market
# You can:

# Create buy and sell orders for resources that will be matched at the end of every tick.
# List your orders and cancel ones you do not longer need
# Set your price for produced electricity


# GET
# /game/{game_id}/market/prices
# Market Prices


# POST
# /game/{game_id}/player/{player_id}/energy/set_price
# Energy Set Price Player


# GET
# /game/{game_id}/orders
# Order List


# GET
# /game/{game_id}/player/{player_id}/orders
# Order List Player


# POST
# /game/{game_id}/player/{player_id}/orders/create
# Order Create Player


# POST
# /game/{game_id}/player/{player_id}/orders/cancel
# Order Cancel Player

# Power plants
# You can:

# Buy more power plants
# Sell power plants
# You can process at most the number of resources per tick as you have power plants of that type
# You can also buy and sell renewables that will produce energy passively


# GET
# /game/{game_id}/player/{player_id}/plant/list
# List Plants


# POST
# /game/{game_id}/player/{player_id}/plant/buy
# Buy Plant


# POST
# /game/{game_id}/player/{player_id}/plant/sell
# Sell Plant


# POST
# /game/{game_id}/player/{player_id}/plant/on
# Turn On


URL = "localhost:8000"

team_secret = "<missing>"
game_id = "1"
player_id = "1"


def set_team_secret():
    global team_secret

    new_team_secret = input("Enter new team secret: ")

    if new_team_secret:
        team_secret = new_team_secret
        print(f"Team secret set to: {team_secret}")
    else:
        print("Team secret not set")


def set_game_id():
    global game_id

    new_game_id = input("Enter new game id: ")

    if new_game_id:
        game_id = new_game_id
        print(f"Game id set to: {game_id}")
    else:
        print("Game id not set")


def set_player_id():
    global player_id

    new_player_id = input("Enter new player id: ")

    if new_player_id:
        player_id = new_player_id
        print(f"Player id set to: {player_id}")
    else:
        print("Player id not set")


def list_games():
    response = requests.get(
        f"http://{URL}/game/list", params={"team_secret": team_secret})

    return response


def list_players():
    response = requests.get(
        f"http://{URL}/game/{game_id}/player/list", params={"team_secret": team_secret})

    return response


def create_player():
    player_name = input("Enter player name: ")

    response = requests.post(f"http://{URL}/game/{game_id}/player/create",
                             params={"team_secret": team_secret},
                             json={"player_name": player_name})

    return response


def get_player():
    response = requests.get(f"http://{URL}/game/{game_id}/player/{player_id}",
                            params={"team_secret": team_secret})

    return response


def delete_player():
    response = requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/delete",
                            params={"team_secret": team_secret})

    return response


def list_orders():
    response = requests.get(f"http://{URL}/game/{game_id}/market/order/list",
                            params={"team_secret": team_secret})

    return response


def list_prices():

    # @router.get("/game/{game_id}/market/prices")
    # async def market_prices(start_tick: int = Query(default=None),
    #                         end_tick: int = Query(default=None),
    #                         resource: Resource = Query(default=None),
    #                         game: Game = Depends(game_dep)) -> Dict[Resource, List[MarketPricesResponse]]:

    start_tick = input("Enter start tick: ")
    end_tick = input("Enter end tick: ")

    response = requests.get(f"http://{URL}/game/{game_id}/market/prices",
                            params={"team_secret": team_secret, "start_tick": start_tick, "end_tick": end_tick})

    return response


def set_energy_price():
    price = input("Enter price: ")

    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/market/energy/set_price",
                             params={"team_secret": team_secret},
                             json={"price": price})

    return response


def create_order():
    available = ["COAL", "URANIUM", "BIOMASS", "GAS", "OIL", "ENERGY"]
    print("Available resources: ", available)
    resource = input("Enter resource: ")
    if resource not in available:
        print("Invalid resource")
        return

    price = input("Enter price: ")
    size = input("Enter size: ")
    expiration_tick = input("Enter expiration tick: ")
    side = input("Enter side (BUY/SELL): ")
    if side not in ["BUY", "SELL"]:
        print("Invalid side")
        return

    order_type = input("Enter order type (LIMIT/MARKET): ")
    if order_type not in ["LIMIT", "MARKET"]:
        print("Invalid order type")
        return

    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/market/order/create",
                             params={"team_secret": team_secret},
                             json={
                                 "resource": resource,
                                 "price": price,
                                 "size": size,
                                 "expiration_tick": expiration_tick,
                                 "side": side,
                                 "type": order_type
                             })

    return response


def list_player_orders():
    response = requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/market/order/list",
                            params={"team_secret": team_secret})

    return response


def cancel_order():
    ids = input("Enter order ids (0,1,2): ")
    ids = list(map(int, ids.split(",")))

    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/market/order/cancel",
                             params={"team_secret": team_secret},
                             json={"ids": ids})

    return response


def list_plants():
    response = requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/plant/list",
                            params={"team_secret": team_secret})

    return response


def buy_plant():
    type = input("Enter plant type: ")
    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/buy",
                             params={"team_secret": team_secret},
                             json={"type": type})

    return response


def sell_plant():
    type = input("Enter plant type: ")
    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/sell",
                             params={"team_secret": team_secret},
                             json={"type": type})

    return response


def turn_on_plant():
    type = input("Enter plant type: ")
    response = requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/on",
                             params={"team_secret": team_secret},
                             json={"type": type})

    return response


def get_dataset():
    start_tick = input("Enter start tick: ")
    end_tick = input("Enter end tick: ")

    response = requests.get(f"http://{URL}/game/{game_id}/dataset",
                            params={"team_secret": team_secret, "start_tick": start_tick, "end_tick": end_tick})

    return response


def main():
    global team_secret, game_id, player_id

    while True:
        try:
            response = get_player()
            if response.status_code != 200:
                raise Exception(
                    f"Player fetching code: {response.status_code}\n{response.json()}")
        except Exception as e:
            print("Error when fetching player")
            print("Please set game id, team secret and player id")
            print("Error: ", e)

        print()
        print("Choose action:")
        print("Current game id: ", game_id)
        print("Current team secret: ", team_secret)
        print("Current player id: ", player_id)
        print(f"1. Enter game id")
        print(f"2. Enter team secret")
        print(f"3. Enter player id")
        print(f"4. List games")
        print(f"5. List players")
        print(f"6. Create player")
        print(f"7. Get player")
        print(f"8. Delete player")
        print(f"9. List orders in market")
        print(f"10. List prices in time period")
        print(f"11. Set energy price for player")
        print(f"12. Create order in market")
        print(f"13. List player orders in market")
        print(f"14. Cancel order in market")
        print(f"15. List plants")
        print(f"16. Buy plant")
        print(f"17. Sell plant")
        print(f"18. Turn on plant")
        print(f"19. Dataset")
        print(f"20. Exit")
        print()

        action = input(">")

        case = {
            "1": set_game_id,
            "2": set_team_secret,
            "3": set_player_id,
            "4": list_games,
            "5": list_players,
            "6": create_player,
            "7": get_player,
            "8": delete_player,
            "9": list_orders,
            "10": list_prices,
            "11": set_energy_price,
            "12": create_order,
            "13": list_player_orders,
            "14": cancel_order,
            "15": list_plants,
            "16": buy_plant,
            "17": sell_plant,
            "18": turn_on_plant,
            "29": get_dataset,
            "20": lambda: exit()
        }

        try:
            response = case[action]()

            if response.status_code != 200:
                print("Error " + response.status_code)
            pprint(response.json())
        except Exception as e:
            print("Error: ", e)

        print()


if __name__ == "__main__":
    main()
