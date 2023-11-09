class PowerPlant:
    def __init__(self, plant_id, plant_type, production_rate, tier=0):
        self.id = plant_id
        self.plant_type = plant_type
        self.production_rate = (2**tier) * production_rate
        self.tier = tier

    def upgrade_production_rate(self, new_production_rate):
        # TODO - discuss should these types of upgrades even be possible
        if new_production_rate > self.production_rate:
            self.production_rate += new_production_rate
            print(
                f'{self.name} upgraded! Production rate increased by: {self.production_rate} MW'
            )
        else:
            print('New production rate must be higher than the current rate.')

    def upgrade_tier(self):
        # TODO - Max tier?
        self.tier += 1


class NuclearPowerPlant(PowerPlant):
    production_rate = 280

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, 'Nuclear', NuclearPowerPlant.production_rate, **kwargs
        )


class HydroPowerPlant(PowerPlant):
    production_rate = 180

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, 'Hydro', HydroPowerPlant.production_rate, **kwargs)


class CoalPowerPlant(PowerPlant):
    production_rate = 120

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, 'Coal', CoalPowerPlant.production_rate, **kwargs)


class GeoThermalPowerPlant(PowerPlant):
    production_rate = 100

    def __init__(self, plant_id, **kwargs):
        super().__init__(
            plant_id, 'GeoThermal', GeoThermalPowerPlant.production_rate, **kwargs
        )


class GasPowerPlant(PowerPlant):
    production_rate = 80

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, 'Gas', GasPowerPlant.production_rate, **kwargs)


class WindPowerPlant(PowerPlant):
    production_rate = 50

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, 'Wind', WindPowerPlant.production_rate, **kwargs)


class SolarPowerPlant(PowerPlant):
    production_rate = 20

    def __init__(self, plant_id, **kwargs):
        super().__init__(plant_id, 'Solar', SolarPowerPlant.production_rate, **kwargs)
