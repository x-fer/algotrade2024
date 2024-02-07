from enum import Enum
from config import config


class PowerPlantType(Enum):
    COAL = 1
    URANIUM = 2
    BIOMASS = 3
    GAS = 4
    OIL = 5
    GEOTHERMAL = 6
    WIND = 7
    SOLAR = 8
    HYDRO = 9

    def get_name(self):
        return self.name.lower()

    def get_base_price(self):
        return config["power_plant"]["base_prices"][self.get_name()]

    def get_warmup_coeff(self):
        return config["power_plant"]["warmup_coeff"][self.get_name()]

    def get_cooldown_coeff(self):
        return config["power_plant"]["cooldown_coeff"][self.get_name()]

    def get_plant_price(self, power_plant_count: int):
        return self.get_base_price() + (5000 * power_plant_count)

    def get_new_temp(self, t0, powered_on):
        if powered_on:
            return cap((1. + t0) * self.get_warmup_coeff() - 1.)
        return cap(t0 * self.get_cooldown_coeff())
    
    def is_renewable(self):
        name = self.get_name()
        return False if name in ["coal", "uranium", "biomass", "gas", "oil"] else True

def cap(x):
    return min(1, max(0, x))

for power_plant_type in PowerPlantType:
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["base_prices"], f"Missing price for {power_plant_type.name}"
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["warmup_coeff"], f"Missing price for {power_plant_type.name}"
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["cooldown_coeff"], f"Missing price for {power_plant_type.name}"

