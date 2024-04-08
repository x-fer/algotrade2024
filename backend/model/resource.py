from enum import Enum


class Resource(Enum):
    COAL = "coal"
    URANIUM = "uranium"
    BIOMASS = "biomass"
    GAS = "gas"
    OIL = "oil"

class Energy(Enum):
    ENERGY = "energy"

class ResourceOrEnergy(Enum):
    COAL = "coal"
    URANIUM = "uranium"
    BIOMASS = "biomass"
    GAS = "gas"
    OIL = "oil"
    ENERGY = "energy"

    def __eq__(self, other) -> bool:
        if isinstance(other, Resource) or isinstance(other, Energy) or isinstance(other, ResourceOrEnergy):
            return self.value == other.value
        return False