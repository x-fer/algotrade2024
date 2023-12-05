from uuid import uuid4, UUID
from powerplants import PowerPlant
from constants import SELLING_COEFFICIENT


class Player:
    START_FUNDS = 1000

    def __init__(
        self, player_id, name, funds=START_FUNDS, power_plants=None, energy_sources=None
    ):
        self.__id = player_id
        self.name = name
        self.funds = funds
        self.energy_output = 0

        if power_plants is None:
            self.power_plants: dict[UUID, PowerPlant] = {}
        else:
            self.power_plants = power_plants

        if energy_sources is None:
            self.energy_sources = {
                "electric": 0,
                "coal": 0,
                "gas": 0,
                "uranium": 0,
            }
        else:
            self.power_plants = power_plants

    # This method should be called after updating any power plant (maybe at the end of a tick, hmm?)
    # To access the Player energy output use ex. 'p1.energy_output'

    def generate_energy(self):
        energy_output = 0
        tmp_energy_sources = self.energy_sources.copy()

        for plant in self.power_plants.values():
            for resource, consume_ammount in plant.consume_source_per_tick.items():
                if tmp_energy_sources[resource] < consume_ammount:
                    tmp_energy_sources[resource] = 0
                    plant.switch_power_plant()
                else:
                    tmp_energy_sources[resource] -= consume_ammount

            energy_output += plant.production_rate

        self.energy_sources - tmp_energy_sources.copy()
        self.energy_output = energy_output

        return energy_output

    def calculate_max_energy_output(self):
        energy_output = sum(
            plant.production_rate for plant in self.power_plants.values()
        )
        self.energy_output = energy_output

        return energy_output

    def buy_power_plants(
        self, power_plant, ammount: int, price_per_unit: float
    ) -> list:
        # TODO - implement correct buying price
        if not issubclass(power_plant, PowerPlant):
            print("Buying object is not a PowerPlant!")
            return []

        if self.funds < ammount * price_per_unit:
            return []

        self.funds -= ammount * price_per_unit

        new_plant_ids = []
        for i in range(ammount):
            plant_id = uuid4()
            self.power_plants[plant_id] = power_plant(plant_id)

            new_plant_ids.append(plant_id)

        self.calculate_total_energy_output()

        return new_plant_ids

    def sell_power_plants(self, power_plant_ids: list, buying_price_per_unit: float):
        # TODO - how should the selling price be calculated?

        for plant_id in power_plant_ids:
            if plant_id not in self.power_plants.keys():
                print(f"You don't have a PowerPlant with ID {plant_id}!")
                return False

        for plant_id in power_plant_ids:
            self.power_plants.pop(plant_id)
            self.funds += SELLING_COEFFICIENT * buying_price_per_unit

        self.calculate_total_energy_output()

        return True

    def upgrade_power_plant_tier(self, plant_id):
        # TODO - How should tier prices be calculated?
        self.power_plants[plant_id].upgrade_tier()
        return

    def __repr__(self):
        return f"Player({self.__id}, {self.name}, {self.funds})"
