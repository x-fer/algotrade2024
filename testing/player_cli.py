from pprint import pprint
import algotrade_api


def input_team_secret():
    new_team_secret = input("Enter new team secret: ")

    if new_team_secret:
        algotrade_api.set_team_secret(new_team_secret)
        print(f"Team secret set to: {new_team_secret}")
    else:
        print("Team secret not set")


def input_game_id():
    new_game_id = input("Enter new game id: ")

    if new_game_id:
        algotrade_api.set_game_id(new_game_id)
        print(f"Game id set to: {new_game_id}")
    else:
        print("Game id not set")


def input_player_id():
    new_player_id = input("Enter new player id: ")

    if new_player_id:
        algotrade_api.set_player_id(new_player_id)
        print(f"Player id set to: {new_player_id}")
    else:
        print("Player id not set")


def create_player():
    player_name = input("Enter player name: ")
    return algotrade_api.create_player(player_name)


def list_prices():
    start_tick = int(input("Enter start tick: "))
    end_tick = int(input("Enter end tick: "))
    return algotrade_api.get_prices(start_tick, end_tick)


def set_energy_price():
    price = input("Enter price: ")
    return algotrade_api.set_energy_price(price)


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

    # order_type = input("Enter order type (LIMIT/MARKET): ")
    # if order_type not in ["LIMIT", "MARKET"]:
    #     print("Invalid order type")
    #     return

    return algotrade_api.create_order(price=price, side=side, size=size,
                                      expiration_tick=expiration_tick,
                                      resource=resource)


def list_orders():
    restriction = input(
        "Restriction on order (all/bot/best): ")
    return algotrade_api.get_orders(restriction=restriction)


def list_player_orders():
    return algotrade_api.get_player_orders()


def cancel_order():
    ids = input("Enter order ids (0,1,2): ")
    ids = list(map(int, ids.split(",")))
    return algotrade_api.cancel_orders(ids)


def buy_plant():
    type = input("Enter plant type: ")
    return algotrade_api.buy_plant(type)


def sell_plant():
    type = input("Enter plant type: ")
    return algotrade_api.sell_plant(type)


def turn_on_plant():
    type = input("Enter plant type: ")
    return algotrade_api.turn_on_plant(type)


def turn_off_plant():
    type = input("Enter plant type: ")
    return algotrade_api.turn_off_plant(type)


def get_dataset():
    start_tick = input("Enter start tick: ")
    end_tick = input("Enter end tick: ")
    return get_dataset(start_tick, end_tick)


def main():
    global team_secret, game_id, player_id

    while True:
        try:
            response = algotrade_api.get_player()
            if response.status_code != 200:
                raise Exception(
                    f"Player fetching code: {response.status_code}\n{response.json()}")
        except Exception as e:
            print("Error when fetching player")
            print("Please set game id, team secret and player id")
            print("Error: ", e)

        print()
        print("Choose action:")
        print("Current game id: ", algotrade_api.game_id)
        print("Current team secret: ", algotrade_api.team_secret)
        print("Current player id: ", algotrade_api.player_id)
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
            "1": input_game_id,
            "2": input_team_secret,
            "3": input_player_id,
            "4": algotrade_api.get_games,
            "5": algotrade_api.get_players,
            "6": create_player,
            "7": algotrade_api.get_player,
            "8": algotrade_api.delete_player,
            "9": list_orders,
            "10": list_prices,
            "11": set_energy_price,
            "12": create_order,
            "13": list_player_orders,
            "14": cancel_order,
            "15": algotrade_api.get_plants,
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
