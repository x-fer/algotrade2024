from dataclasses import dataclass, field
from db.table import Table
from enum import Enum
from config import config
from model.resource import Resource
from model.dataset_data import DatasetData


class PowerPlantType(str, Enum):
    COAL = "COAL"
    URANIUM = "URANIUM"
    BIOMASS = "BIOMASS"
    GAS = "GAS"
    OIL = "OIL"
    GEOTHERMAL = "GEOTHERMAL"
    WIND = "WIND"
    SOLAR = "SOLAR"
    HYDRO = "HYDRO"

    def get_name(self):
        return self.name.lower()

    def get_base_price(self):
        return config["power_plant"]["base_prices"][self.get_name()]

    def get_plant_price(self, power_plant_count: int):
        return int(self.get_base_price() * (1 + config["power_plant"]["price_coeff"] * power_plant_count))

    def get_sell_price(self, power_plant_count: int):
        plant_price = self.get_plant_price(power_plant_count - 1)
        sell_plant_price = round(
            plant_price * config["power_plant"]["sell_coeff"])

        return sell_plant_price

    def get_produced_energy(self, dataset_row: dict):
        return dataset_row[self.get_name()]

    def is_renewable(self):
        name = self.get_name()
        return False if name in ["coal", "uranium", "biomass", "gas", "oil"] else True


@dataclass
class Player(Table):
    table_name = "players"
    player_id: int
    player_name: str
    game_id: int
    team_id: int
    is_active: bool = field(default=True)
    is_bot: bool = field(default=False)

    energy_price: int = field(default=1e9)

    money: int = field(default=0)
    energy: int = field(default=0)

    coal: int = field(default=0)
    uranium: int = field(default=0)
    biomass: int = field(default=0)
    gas: int = field(default=0)
    oil: int = field(default=0)

    coal_plants_owned: int = field(default=0)
    uranium_plants_owned: int = field(default=0)
    biomass_plants_owned: int = field(default=0)
    gas_plants_owned: int = field(default=0)
    oil_plants_owned: int = field(default=0)
    geothermal_plants_owned: int = field(default=0)
    wind_plants_owned: int = field(default=0)
    solar_plants_owned: int = field(default=0)
    hydro_plants_owned: int = field(default=0)

    coal_plants_powered: int = field(default=0)
    uranium_plants_powered: int = field(default=0)
    biomass_plants_powered: int = field(default=0)
    gas_plants_powered: int = field(default=0)
    oil_plants_powered: int = field(default=0)
    geothermal_plants_powered: int = field(default=0)
    wind_plants_powered: int = field(default=0)
    solar_plants_powered: int = field(default=0)
    hydro_plants_powered: int = field(default=0)

    def __getitem__(self, key):
        if isinstance(key, Resource):
            return self.__getattribute__(key.name)
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        if isinstance(key, Resource):
            return self.__setattr__(key.name, value)
        self.__setattr__(key, value)

    async def get_networth(self, game):
        net_worth = {
            "plants_owned": {},
            "money": self.money,
            "resources": {},
            "total": 0
        }

        for type in PowerPlantType:
            value = 0

            for i in range(1, getattr(self, f"{type.lower()}_plants_owned") + 1):
                value += type.get_sell_price(i)

            net_worth["plants_owned"][type.lower()] = {
                "owned": getattr(self, f"{type.lower()}_plants_owned"),
                "value_if_sold": value
            }

        data = (await DatasetData.list_by_game_id_where_tick(
            game.dataset_id, game.game_id, game.current_tick - 1, game.current_tick - 1))[0]

        for resource in Resource:
            final_price = data[f"{resource.name.lower()}_price"]
            has = getattr(self, resource.name.lower())

            net_worth["resources"][resource.name.lower()] = {
                "final_price": final_price,
                "player_has": has,
                "value": final_price * has
            }

        net_worth["total"] += self.money
        for type in PowerPlantType:
            net_worth["total"] += net_worth["plants_owned"][type.lower()
                                                            ]["value_if_sold"]

        for resource in Resource:
            net_worth["total"] += net_worth["resources"][resource.name.lower()
                                                         ]["value"]

        return net_worth
