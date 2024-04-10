from enum import Enum

from config import config


class PowerPlantType(str, Enum):
    COAL = "coal"
    URANIUM = "uranium"
    BIOMASS = "biomass"
    GAS = "gas"
    OIL = "oil"
    GEOTHERMAL = "geothermal"
    WIND = "wind"
    SOLAR = "solar"
    HYDRO = "hydro"

    def _get_config_name(self):
        return self.name.lower()

    def get_base_price(self):
        return config["power_plant"]["base_prices"][self._get_config_name()]

    def get_plant_price(self, power_plant_count: int):
        return int(
            self.get_base_price()
            * (1 + 0.03 * (power_plant_count**2) + 0.1 * power_plant_count)
        )

    def get_sell_price(self, power_plant_count: int):
        plant_price = self.get_plant_price(power_plant_count - 1)
        sell_plant_price = round(plant_price * config["power_plant"]["sell_coeff"])

        return sell_plant_price

    def is_renewable(self):
        name = self._get_config_name()
        return False if name in ["coal", "uranium", "biomass", "gas", "oil"] else True
