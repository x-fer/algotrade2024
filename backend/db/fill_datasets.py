import os
import pandas as pd
from model import Datasets, DatasetData
from datetime import datetime
from config import config
from logger import logger


datasets_path = config["dataset"]["datasets_path"]


async def fill_datasets():
    logger.info("Filling datasets")
    for dataset in os.listdir(datasets_path):

        if not dataset.endswith(".csv"):
            continue
        try:
            await Datasets.get(dataset_name=dataset)
            logger.debug(f"Dataset {dataset} already created")
            continue
        except Exception as e:

            pass

        df = pd.read_csv(f"{datasets_path}/{dataset}")

        # TODO: asserts, async transaction - ne zelimo da se dataset kreira ako faila kreiranje redaka
        dataset_id = await Datasets.create(dataset_name=dataset, dataset_description="Opis")

        price_multipliers = config["dataset"]["price_multiplier"]
        energy_output_multipliers = config["dataset"]["energy_output_multiplier"]
        energy_demand_multiplier = config["dataset"]["energy_demand_multiplier"]

        # date,COAL,URANIUM,BIOMASS,GAS,OIL,GEOTHERMAL,WIND,SOLAR,HYDRO,ENERGY_DEMAND,MAX_ENERGY_PRICE
        tick = 0
        dataset_data = []
        for index, row in df.iterrows():
            dataset_data.append(DatasetData(
                dataset_data_id=0,
                dataset_id=dataset_id,
                tick=tick,
                date=datetime.strptime(
                    row["date"], "%Y-%m-%d %H:%M:%S"),
                coal=(
                    energy_output_multipliers["coal"] *
                    row["COAL"] // 1_000_000),
                uranium=(
                    energy_output_multipliers["uranium"] *
                    row["URANIUM"] // 1_000_000),
                biomass=(
                    energy_output_multipliers["biomass"] *
                    row["BIOMASS"] // 1_000_000),
                gas=(
                    energy_output_multipliers["gas"] *
                    row["GAS"] // 1_000_000),
                oil=(
                    energy_output_multipliers["oil"] *
                    row["OIL"] // 1_000_000),
                geothermal=(
                    energy_output_multipliers["geothermal"] *
                    row["GEOTHERMAL"] // 1_000_000),
                wind=(
                    energy_output_multipliers["wind"] *
                    row["WIND"] // 1_000_000),
                solar=(
                    energy_output_multipliers["solar"] *
                    row["SOLAR"] // 1_000_000),
                hydro=(
                    energy_output_multipliers["hydro"] *
                    row["HYDRO"] // 1_000_000),
                energy_demand=(
                    energy_demand_multiplier *
                    row["ENERGY_DEMAND"] // 1_000_000),
                max_energy_price=(
                    price_multipliers["energy"] *
                    row["MAX_ENERGY_PRICE"] // 1_000_000),
                coal_price=(
                    price_multipliers["coal"] *
                    row["COAL_PRICE"] // 1_000_000),
                uranium_price=(
                    price_multipliers["uranium"] *
                    row["URANIUM_PRICE"] // 1_000_000),
                biomass_price=(
                    price_multipliers["biomass"] *
                    row["BIOMASS_PRICE"] // 1_000_000),
                gas_price=(
                    price_multipliers["gas"] *
                    row["GAS_PRICE"] // 1_000_000),
                oil_price=(
                    price_multipliers["oil"] *
                    row["OIL_PRICE"] // 1_000_000),
            ))
            tick += 1

        for x in dataset_data:
            assert x.coal_price > -config["bots"]["min_price"]
            assert x.uranium_price > -config["bots"]["min_price"]
            assert x.biomass_price > -config["bots"]["min_price"]
            assert x.gas_price > -config["bots"]["min_price"]
            assert x.oil_price > -config["bots"]["min_price"]

        await DatasetData.create_many(dataset_data)
        logger.info(f"Added dataset {dataset}")
