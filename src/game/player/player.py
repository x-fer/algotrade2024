from uuid import uuid4, UUID
from powerplants import PowerPlant


class Player:
    START_FUNDS = 1000

    def __init__(self, player_id, name, funds=START_FUNDS, power_plants=None):
        self.__id = player_id
        self.name = name
        self.funds = funds
        self.energy_output = 0

        if power_plants is None:
            self.power_plants: dict[UUID, PowerPlant] = {}
        else:
            self.power_plants = power_plants

    # This method should be called after updating any power plant (maybe at the end of a tick, hmm?)
    # To access the Player energy output use ex. 'p1.energy_output'
    def calculate_total_energy_output(self):
        energy_output = sum(
            plant.production_rate for plant in self.power_plants.values()
        )
        self.energy_output = energy_output
        return

    def buy_power_plants(self, power_plant, ammount, price_per_unit) -> bool:
        if not issubclass(power_plant, PowerPlant):
            print("Invalid power plant instance!")
            return False

        if self.funds < ammount * price_per_unit:
            return False

        self.funds -= ammount * price_per_unit
        for i in range(ammount):
            plant_id = uuid4()
            self.power_plants[plant_id] = power_plant(plant_id)

        self.calculate_total_energy_output()
        return True

    def sell_power_plant(self, power_plant):
        # TODO - Add selling of power plant
        # - how should the selling price be calculated?
        return

    def upgrade_power_plant_tier(self, plant_id):
        # TODO - How should tier prices be calculated?
        self.power_plants[plant_id].upgrade_tier()
        return

    def __repr__(self):
        return f"Player({self.__id}, {self.name}, {self.funds})"
