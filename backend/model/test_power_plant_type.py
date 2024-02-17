import pytest
from model import PowerPlantType
from model.power_plant_types import cap
from config import config


@pytest.mark.parametrize("power_plant_type", list(PowerPlantType))
def test_power_plant_type_config(power_plant_type):
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["base_prices"], f"Missing price for {power_plant_type.name}"
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["warmup_coeff"], f"Missing warm-up coefficient for {power_plant_type.name}"
    assert power_plant_type.name.lower(
    ) in config["power_plant"]["cooldown_coeff"], f"Missing cooldown coefficient for {power_plant_type.name}"


def test_power_plant_type_methods():
    # Test get_name method
    assert PowerPlantType.COAL.get_name() == "coal"

    # Test get_base_price method (assuming the configuration is properly set)
    assert PowerPlantType.COAL.get_base_price(
    ) == config["power_plant"]["base_prices"]["coal"]

    # Test get_warmup_coeff method
    assert PowerPlantType.COAL.get_warmup_coeff(
    ) == config["power_plant"]["warmup_coeff"]["coal"]

    # Test get_cooldown_coeff method
    assert PowerPlantType.COAL.get_cooldown_coeff(
    ) == config["power_plant"]["cooldown_coeff"]["coal"]

    # Test get_plant_price method
    # Assuming power_plant_count is 2 for testing
    assert PowerPlantType.COAL.get_plant_price(
        2) == config["power_plant"]["base_prices"]["coal"] + 10000

    # Test get_new_temp method
    # Assuming t0 is 0.5 and powered_on is True for testing
    assert PowerPlantType.COAL.get_new_temp(0.5, True) == cap(
        (1. + 0.5) * config["power_plant"]["warmup_coeff"]["coal"] - 1.)

    # Test get_new_temp method when powered_on is False
    # Assuming t0 is 0.5 for testing
    assert PowerPlantType.COAL.get_new_temp(0.5, False) == cap(
        0.5 * config["power_plant"]["cooldown_coeff"]["coal"])

    # Test is_renewable method for COAL (non-renewable)
    assert PowerPlantType.COAL.is_renewable() is False

    # Test is_renewable method for WIND (renewable)
    assert PowerPlantType.WIND.is_renewable() is True


def test_cap_function():
    # Test cap function for various input values
    assert cap(0.5) == 0.5
    assert cap(1.5) == 1
    assert cap(-0.5) == 0
