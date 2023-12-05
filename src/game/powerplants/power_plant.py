class PowerPlant:
    def __init__(
        self,
        plant_id,
        plant_type,
        production_rate,
        consume_source_per_tick: dict,
        tier=0,
    ):
        self.id = plant_id
        self.plant_type = plant_type
        self.plant_state = 0

        self.production_rate = (2**tier) * production_rate * self.plant_state
        self.consume_source_per_tick = consume_source_per_tick
        self.tier = tier

    # Turning power plant ON/OFF
    # TODO - add switching costs based on plant type
    def switch_power_plant(self):
        if self.plant_state == 0:
            self.plant_state = 1
        else:
            self.plant_state = 0

    def upgrade_production_rate(self, new_production_rate):
        # TODO - discuss should these types of upgrades even be possible
        if new_production_rate > self.production_rate:
            self.production_rate += new_production_rate
            print(
                f"{self.name} upgraded! Production rate increased by: {self.production_rate} MW"
            )
        else:
            print("New production rate must be higher than the current rate.")

    def upgrade_tier(self):
        # TODO - Max tier?
        self.tier += 1


class NuclearPowerPlant(PowerPlant):
    base_production_rate = 280
    consume_source_per_tick = {"uranium": 1, "electric": 5}

    def __init__(self, plant_id, *args, **kwargs):
        super().__init__(
            plant_id, "Nuclear", NuclearPowerPlant.base_production_rate, *args, **kwargs
        )


class HydroPowerPlant(PowerPlant):
    base_production_rate = 180
    consume_source_per_tick = {"electric": 4}

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, "Hydro", HydroPowerPlant.base_production_rate, **kwargs
        )


class CoalPowerPlant(PowerPlant):
    base_production_rate = 120
    consume_source_per_tick = {"coal": 1, "electric": 4}

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, "Coal", CoalPowerPlant.base_production_rate, **kwargs
        )


class GeoThermalPowerPlant(PowerPlant):
    base_production_rate = 100
    consume_source_per_tick = {"electric": 2}

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, "GeoThermal", GeoThermalPowerPlant.base_production_rate, **kwargs
        )


class GasPowerPlant(PowerPlant):
    base_production_rate = 80
    consume_source_per_tick = {"gas": 3, "electric": 2}

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, "Gas", GasPowerPlant.base_production_rate, **kwargs)


class WindPowerPlant(PowerPlant):
    base_production_rate = 50
    consume_source_per_tick = {"electric": 1}

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, "Wind", WindPowerPlant.base_production_rate, **kwargs
        )


class SolarPowerPlant(PowerPlant):
    base_production_rate = 20
    consume_source_per_tick = {}

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, "Solar", SolarPowerPlant.base_production_rate, **kwargs
        )
