from dataclasses import dataclass, field
from db.table import Table
from enum import Enum
from config import config


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
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
