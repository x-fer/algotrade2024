import pytest
from model import PowerPlant, Player, PowerPlantType


@pytest.fixture
def sample_power_plant():
    return PowerPlant(
        power_plant_id=1,
        type=PowerPlantType.COAL,
        player_id=1,
        price=100
    )


@pytest.fixture
def sample_renewable_power_plant():
    return PowerPlant(
        power_plant_id=2,
        type=PowerPlantType.WIND,
        player_id=2,
        price=150
    )


@pytest.fixture
def sample_player():
    return Player(
        player_id=1,
        player_name="John",
        game_id=1,
        team_id=1,
        energy=2,
        coal=3,
    )


def test_power_plant_initialization(sample_power_plant):
    assert sample_power_plant.power_plant_id == 1
    assert sample_power_plant.type == PowerPlantType.COAL
    assert sample_power_plant.player_id == 1
    assert sample_power_plant.price == 100
    assert sample_power_plant.powered_on is False
    assert sample_power_plant.temperature == 0


def test_power_plant_has_resources(sample_power_plant, sample_renewable_power_plant, sample_player):
    assert sample_power_plant.has_resources(sample_player) is True

    # Renewable power plant should always have resources
    assert sample_renewable_power_plant.has_resources(sample_player) is True

    # Ensure that player's coal resource count is not enough for non-renewable power plant
    sample_player.coal = 0
    assert sample_power_plant.has_resources(sample_player) is False


def test_power_plant_get_produced_energy(sample_power_plant, sample_renewable_power_plant, sample_player):
    # Test for non-renewable power plant
    dataset_row = {'COAL': 50}
    assert sample_power_plant.get_produced_energy(dataset_row) == 50

    # Test for renewable power plant
    dataset_row = {'WIND': 30}
    assert sample_renewable_power_plant.get_produced_energy(dataset_row) == 30
