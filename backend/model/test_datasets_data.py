import pytest
from model import DatasetData


@pytest.fixture
def sample_dataset_data():
    return DatasetData(
        dataset_data_id=1,
        dataset_id=1,
        date="2024-02-16",
        tick=1,
        coal=100,
        uranium=50,
        biomass=30,
        gas=80,
        oil=70,
        geothermal=20,
        wind=40,
        solar=60,
        hydro=25,
        energy_demand=300,
        max_energy_price=70
    )


def test_dataset_data_initialization(sample_dataset_data):
    assert sample_dataset_data.dataset_data_id == 1
    assert sample_dataset_data.dataset_id == 1
    assert sample_dataset_data.date == "2024-02-16"
    assert sample_dataset_data.tick == 1
    assert sample_dataset_data.coal == 100
    assert sample_dataset_data.uranium == 50
    assert sample_dataset_data.biomass == 30
    assert sample_dataset_data.gas == 80
    assert sample_dataset_data.oil == 70
    assert sample_dataset_data.geothermal == 20
    assert sample_dataset_data.wind == 40
    assert sample_dataset_data.solar == 60
    assert sample_dataset_data.hydro == 25
    assert sample_dataset_data.energy_demand == 300
    assert sample_dataset_data.max_energy_price == 70


def test_dataset_data_indexing(sample_dataset_data):
    assert sample_dataset_data['Coal'] == 100
    assert sample_dataset_data['uranium'] == 50
    assert sample_dataset_data['biomass'] == 30
    assert sample_dataset_data['gas'] == 80
    assert sample_dataset_data['Oil'] == 70
    assert sample_dataset_data['geothermal'] == 20
    assert sample_dataset_data['Wind'] == 40
    assert sample_dataset_data['SOLAR'] == 60
    assert sample_dataset_data['Hydro'] == 25
    assert sample_dataset_data['energy_demand'] == 300
    assert sample_dataset_data['max_energy_price'] == 70
