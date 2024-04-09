import os
import pandas as pd
from model import Datasets, DatasetData
from datetime import datetime
from config import config
from logger import logger
from redlock.lock import RedLock

from model.power_plant_model import PowerPlantsModel, ResourcesModel
from model.power_plant_type import PowerPlantType
from model.resource import Resource


datasets_path = config["dataset"]["datasets_path"]
price_multipliers = config["dataset"]["price_multiplier"]
energy_output_multipliers = config["dataset"]["energy_output_multiplier"]
energy_demand_multiplier = config["dataset"]["energy_demand_multiplier"]


def fill_datasets():
    logger.info("Filling datasets")
    pipe = DatasetData.db().pipeline()
    for dataset_name in os.listdir(datasets_path):
        if not dataset_name.endswith(".csv"):
            continue
        if Datasets.find(Datasets.dataset_name == dataset_name).count() > 0:
            logger.info(f"Dataset {dataset_name} already created")
            continue

        df = pd.read_csv(f"{datasets_path}/{dataset_name}")

        dataset = Datasets(dataset_name=dataset_name, dataset_description="Opis")
        dataset.save()

        tick = 0
        for _, row in df.iterrows():
            from_row(dataset, tick, row).save(pipe)
            tick += 1
        logger.info(f"Added dataset {dataset_name}")
    pipe.execute()


def from_row(dataset: Datasets, tick: int, row: pd.Series) -> DatasetData:
    power_plants_output = PowerPlantsModel(
        coal=(energy_output_multipliers["coal"] * row["COAL"] // 1_000_000),
        uranium=(energy_output_multipliers["uranium"] * row["URANIUM"] // 1_000_000),
        biomass=(energy_output_multipliers["biomass"] * row["BIOMASS"] // 1_000_000),
        gas=(energy_output_multipliers["gas"] * row["GAS"] // 1_000_000),
        oil=(energy_output_multipliers["oil"] * row["OIL"] // 1_000_000),
        geothermal=(
            energy_output_multipliers["geothermal"] * row["GEOTHERMAL"] // 1_000_000
        ),
        wind=(energy_output_multipliers["wind"] * row["WIND"] // 1_000_000),
        solar=(energy_output_multipliers["solar"] * row["SOLAR"] // 1_000_000),
        hydro=(energy_output_multipliers["hydro"] * row["HYDRO"] // 1_000_000),
    )
    resource_prices = ResourcesModel(
        coal=(price_multipliers["coal"] * row["COAL_PRICE"] // 1_000_000),
        uranium=(
            price_multipliers["uranium"] * row["URANIUM_PRICE"] // 1_000_000
        ),
        biomass=(
            price_multipliers["biomass"] * row["BIOMASS_PRICE"] // 1_000_000
        ),
        gas=(price_multipliers["gas"] * row["GAS_PRICE"] // 1_000_000),
        oil=(price_multipliers["oil"] * row["OIL_PRICE"] // 1_000_000),
    )
    for type in PowerPlantType:
        assert power_plants_output[type] >= 0
    for resource in Resource:
        assert resource_prices[resource] > 0
    return DatasetData(
        dataset_id=dataset.pk,
        tick=tick,
        date=datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S"),
        
        energy_demand=(energy_demand_multiplier * row["ENERGY_DEMAND"] // 1_000_000),
        max_energy_price=(
            price_multipliers["energy"] * row["MAX_ENERGY_PRICE"] // 1_000_000
        ),
        power_plants_output = power_plants_output,
        resource_prices = resource_prices
    )
