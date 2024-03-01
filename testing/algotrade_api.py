from pprint import pprint
import requests


URL = "localhost:8000"

team_secret = "<missing>"
game_id = "1"
player_id = "1"


def set_url(new_URL):
    global URL
    URL = new_URL


def set_team_secret(new_team_secret):
    global team_secret
    team_secret = new_team_secret


def set_game_id(new_game_id):
    global game_id
    game_id = new_game_id


def set_player_id(new_player_id):
    global player_id
    player_id = new_player_id


class Resource():
    energy = "ENERGY"
    coal = "COAL"
    uranium = "URANIUM"
    biomass = "BIOMASS"
    gas = "GAS"
    oil = "OIL"


class PowerPlant():
    COAL = "COAL"
    URANIUM = "URANIUM"
    BIOMASS = "BIOMASS"
    GAS = "GAS"
    OIL = "OIL"
    GEOTHERMAL = "GEOTHERMAL"
    WIND = "WIND"
    SOLAR = "SOLAR"
    HYDRO = "HYDRO"


class OrderSide():
    BUY = "BUY"
    SELL = "SELL"


def get_games():
    return requests.get(f"http://{URL}/game/list",
                        params={"team_secret": team_secret})


def get_game():
    return requests.get(f"http://{URL}/game/{game_id}",
                        params={"team_secret": team_secret})


def get_players():
    return requests.get(f"http://{URL}/game/{game_id}/player/list",
                        params={"team_secret": team_secret})


def create_player(player_name: str = None):
    return requests.post(
        f"http://{URL}/game/{game_id}/player/create",
        params={"team_secret": team_secret},
        json={"player_name": player_name})


def get_player():
    return requests.get(f"http://{URL}/game/{game_id}/player/{player_id}",
                        params={"team_secret": team_secret})


def delete_player():
    return requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/delete",
                        params={"team_secret": team_secret})


def get_orders():
    return requests.get(f"http://{URL}/game/{game_id}/orders",
                        params={"team_secret": team_secret})


def get_player_orders():
    return requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/orders",
                        params={"team_secret": team_secret})


def get_prices(start_tick=None, end_tick=None, resource=None):
    url = f"{URL}/game/{game_id}/market/prices"
    params = {"team_secret": team_secret}
    if start_tick:
        params["start_tick"] = start_tick
    if end_tick:
        params["end_tick"] = end_tick
    if resource:
        params["resource"] = resource
    return requests.get(url, params=params)


def set_energy_price(price):
    requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/energy/set_price",
                  params={"team_secret": team_secret},
                  json={"price": price})


def create_order(resource, price, size, expiration_tick, side):
    body = {
        "resource": resource,
        "price": price,
        "size": size,
        "expiration_tick": expiration_tick,
        "side": side
    }
    requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/orders/create",
                  params={"team_secret": team_secret}, json=body)


def cancel_orders(ids):
    return requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/market/order/cancel",
                         params={"team_secret": team_secret},
                         json={"ids": ids})


def get_plants():
    return requests.get(f"http://{URL}/game/{game_id}/player/{player_id}/plant/list",
                        params={"team_secret": team_secret})


def buy_plant(type):
    return requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/buy",
                         params={"team_secret": team_secret},
                         json={"type": type})


def sell_plant(type):
    return requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/sell",
                         params={"team_secret": team_secret},
                         json={"type": type})


def turn_on_plant(type):
    return requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/on",
                         params={"team_secret": team_secret},
                         json={"type": type})


def turn_off_plant(type):
    return requests.post(f"http://{URL}/game/{game_id}/player/{player_id}/plant/off",
                         params={"team_secret": team_secret},
                         json={"type": type})


def get_dataset(start_tick=None, end_tick=None):
    url = f"{URL}/game/{game_id}/dataset"
    params = {"team_secret": team_secret}
    if start_tick:
        params["start_tick"] = start_tick
    if end_tick:
        params["end_tick"] = end_tick
    return requests.get(url, params=params).json()
