from enum import Enum
from pprint import pprint
import requests


class Resource(Enum):
    energy = "ENERGY"
    coal = "COAL"
    uranium = "URANIUM"
    biomass = "BIOMASS"
    gas = "GAS"
    oil = "OIL"


class PowerPlant(Enum):
    COAL = "COAL"
    URANIUM = "URANIUM"
    BIOMASS = "BIOMASS"
    GAS = "GAS"
    OIL = "OIL"
    GEOTHERMAL = "GEOTHERMAL"
    WIND = "WIND"
    SOLAR = "SOLAR"
    HYDRO = "HYDRO"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class AlgotradeApi:
    def __init__(self, url, team_secret, game_id, player_id=None):
        self.team_secret = team_secret
        self.URL = url

        self.team_secret = team_secret
        self.game_id = game_id
        self.player_id = player_id

    def set_url(self, new_URL):
        self.URL = new_URL

    def set_team_secret(self, new_team_secret):
        self.team_secret = new_team_secret

    def set_game_id(self, new_game_id):
        self.game_id = new_game_id

    def set_player_id(self, new_player_id):
        self.player_id = new_player_id

    def get_games(self):
        return requests.get(f"http://{self.URL}/game/list",
                            params={"team_secret": self.team_secret})

    def get_game(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}",
                            params={"team_secret": self.team_secret})

    def get_players(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/list",
                            params={"team_secret": self.team_secret})

    def create_player(self, player_name: str = None):
        return requests.post(
            f"http://{self.URL}/game/{self.game_id}/player/create",
            params={"team_secret": self.team_secret},
            json={"player_name": player_name})

    def reset_player(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/reset",
                            params={"team_secret": self.team_secret})

    def get_player(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}",
                            params={"team_secret": self.team_secret})

    def delete_player(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/delete",
                            params={"team_secret": self.team_secret})

    def get_orders(self, restriction=None):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/orders",
                            params={"team_secret": self.team_secret,
                                    "restriction": restriction})

    def get_player_orders(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/orders",
                            params={"team_secret": self.team_secret})

    def get_prices(self, start_tick=None, end_tick=None, resource=None):
        url = f"http://{self.URL}/game/{self.game_id}/market/prices"
        params = {"team_secret": self.team_secret}
        if start_tick:
            params["start_tick"] = start_tick
        if end_tick:
            params["end_tick"] = end_tick
        if resource:
            params["resource"] = resource
        return requests.get(url, params=params)

    def set_energy_price(self, price):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/energy/set_price",
                             params={"team_secret": self.team_secret},
                             json={"price": price})

    def create_order(self, resource, price, size, side, expiration_tick=None, expiration_length=None):
        body = {
            "resource": resource,
            "price": price,
            "size": size,
            "expiration_tick": expiration_tick,
            "expiration_length": expiration_length,
            "side": side
        }
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/orders/create",
                             params={"team_secret": self.team_secret}, json=body)

    def cancel_orders(self, ids):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/orders/cancel",
                             params={"team_secret": self.team_secret},
                             json={"ids": ids})

    def get_trades(self, start_tick=None, end_tick=None, resource=None):
        url = f"http://{URL}/game/{self.game_id}/player/{self.player_id}/trades"
        params = {"team_secret": self.team_secret}
        if start_tick:
            params["start_tick"] = start_tick
        if end_tick:
            params["end_tick"] = end_tick
        params["resource"] = resource
        return requests.get(url, params=params)

    def get_plants(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/list",
                            params={"team_secret": self.team_secret})

    def buy_plant(self, type):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/buy",
                             params={"team_secret": self.team_secret},
                             json={"type": type})

    def sell_plant(self, type):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/sell",
                             params={"team_secret": self.team_secret},
                             json={"type": type})

    def turn_on_plant(self, type, number):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/on",
                             params={"team_secret": self.team_secret},
                             json={"type": type, "number": number})

    def get_dataset(self, start_tick=None, end_tick=None):
        url = f"http://{self.URL}/game/{self.game_id}/dataset"
        params = {"team_secret": self.team_secret}
        if start_tick:
            params["start_tick"] = start_tick
        if end_tick:
            params["end_tick"] = end_tick
        return requests.get(url, params=params)

    def get_plant_prices(self):
        return requests.get(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/list",
                            params={"team_secret": self.team_secret})

    def turn_on(self, plant_type, number):
        return requests.post(f"http://{self.URL}/game/{self.game_id}/player/{self.player_id}/plant/on",
                             params={"team_secret": self.team_secret},
                             json={"type": plant_type, "number": number})
