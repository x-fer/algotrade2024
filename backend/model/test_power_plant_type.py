import pytest
from model.player import PowerPlantType
from config import config


def test_get_name():
    assert PowerPlantType.COAL.get_name() == 'coal'


def test_get_base_price():
    assert PowerPlantType.COAL.get_base_price(
    ) == config["power_plant"]["base_prices"]["coal"]


def test_get_warmup_coeff():
    assert PowerPlantType.COAL.get_warmup_coeff(
    ) == config["power_plant"]["warmup_coeff"]["coal"]


def test_get_cooldown_coeff():
    assert PowerPlantType.COAL.get_cooldown_coeff(
    ) == config["power_plant"]["cooldown_coeff"]["coal"]


def test_get_plant_price():
    assert PowerPlantType.COAL.get_plant_price(
        2) == config["power_plant"]["base_prices"]["coal"] + (5000 * 2)


def test_get_produced_energy():
    # Mocking dataset_row
    dataset_row = {'coal': 10, 'uranium': 20, 'biomass': 30}
    assert PowerPlantType.COAL.get_produced_energy(
        dataset_row) == dataset_row["coal"]


def test_is_renewable():
    assert PowerPlantType.COAL.is_renewable() == False
    assert PowerPlantType.SOLAR.is_renewable() == True
