
import numpy as np
import pandas as pd

datasets = [
    "../dataset/chunks/df_2431_2011-11-06 03:30:00_2012-02-15 09:30:00.csv",
    "../dataset/chunks/df_2739_2014-11-02 02:30:00_2015-02-24 04:30:00.csv",
    "../dataset/chunks/df_3023_2012-11-04 03:30:00_2013-03-10 01:30:00.csv",
    "../dataset/chunks/df_3023_2013-11-03 03:30:00_2014-03-09 01:30:00.csv",
    "../dataset/chunks/df_3024_2016-11-06 02:30:00_2017-03-12 01:30:00.csv",
    "../dataset/chunks/df_3477_2018-03-11 04:30:00_2018-08-03 00:30:00.csv",
    "../dataset/chunks/df_4375_2015-05-02 19:30:00_2015-11-01 01:30:00.csv",
    "../dataset/chunks/df_4670_2014-04-21 12:30:00_2014-11-02 01:30:00.csv",
    "../dataset/chunks/df_5484_2016-03-13 04:30:00_2016-10-27 15:30:00.csv",
    "../dataset/chunks/df_5512_2012-03-19 10:30:00_2012-11-04 01:30:00.csv",
    "../dataset/chunks/df_5710_2011-03-13 04:30:00_2011-11-06 01:30:00.csv",
    "../dataset/chunks/df_5710_2013-03-10 04:30:00_2013-11-03 01:30:00.csv",
    "../dataset/chunks/df_5710_2017-03-12 04:30:00_2017-11-05 01:30:00.csv",
]


price_multiplier = {
    "coal": 20000,
    "uranium": 120000,
    "biomass": 60000,
    "gas": 50700,
    "oil": 60000,
    "energy": 500
}

energy_output_multiplier = {
    "coal": 115,
    "uranium": 1500,
    "biomass": 130,
    "gas": 300,
    "oil": 380,
    "geothermal": 30,
    "wind": 40,
    "solar": 35,
    "hydro": 130
}

energy_demand_multiplier = 30000


base_prices = {
    "coal": 3025000,
    "uranium": 97500000,
    "biomass": 9680000,
    "gas": 9704000,
    "oil": 9680000,
    "geothermal": 4000000,
    "wind": 2000000,
    "solar": 1000000,
    "hydro": 12007999
}
sell_coeff = 0.7

start_money = 50_000_000

monopole = 0.3


def get_plant_price(has_plants, resource):
    base = base_prices[resource.lower()]

    return int(base * (1 + 0.03 * (has_plants ** 2) + 0.1 * has_plants))


def get_sell_price(power_plant_count: int, resource: str) -> int:
    plant_price = get_plant_price(power_plant_count - 1, resource)
    sell_plant_price = round(plant_price * sell_coeff)

    return sell_plant_price


def get_networth(df, money, has_plants, resource):

    plant_prices = 0

    for i in range(1, has_plants + 1):
        plant_prices += get_sell_price(i, resource)

    x = df.to_dict('records')[-1]

    if resource in ["COAL", "URANIUM" "BIOMASS", "GAS", "OIL"]:
        return money + plant_prices + has_plants * (x[f"{resource}_PRICE"] *
                                                    price_multiplier[resource.lower()] // 1000000)

    return money + plant_prices


def main():

    for dataset_path in datasets:

        # print("Dataset:", dataset_path)

        df = pd.read_csv(dataset_path)

        df = df[:1800]

        # for resource in ["COAL", "URANIUM", "BIOMASS", "GAS", "OIL", "WIND", "SOLAR", "HYDRO"]:
        for resource in ["SOLAR"]:
            money = start_money
            burned_total = 0
            has_plants = 0

            for x in df.to_dict('records'):

                price = get_plant_price(has_plants, resource)

                max_energy_price = (x["MAX_ENERGY_PRICE"] *
                                    price_multiplier["energy"] // 1000000)

                # energy_price = max_energy_price * 0.90
                energy_price = np.random.randint(400, 500)

                energy_output = energy_output_multiplier[
                    resource.lower()
                ] * x[resource] // 1000000

                max_demand = 0.15 * (energy_demand_multiplier *
                                     x["ENERGY_DEMAND"] // 1000000)

                burned = min(has_plants, max_demand//(energy_output + 0.0001))
                burned_total += burned

                if resource in ["COAL", "URANIUM" "BIOMASS", "GAS", "OIL"]:
                    money -= has_plants * (x[f"{resource}_PRICE"] *
                                           price_multiplier[resource.lower()] // 1000000)

                produced_energy = burned * energy_output

                if money >= price and burned == has_plants:
                    has_plants += 1
                    money -= price

                # if money >= price and burned != has_plants:
                #     print("[W]", end="")

                if energy_price <= max_energy_price and np.random.uniform(0, 1) > 0.2:
                    money += produced_energy * energy_price

                # print("Money:", money, "Burned_total:", burned_total, "Has_plants:", has_plants)

            print("Resource:", resource,
                  "Has plants:", has_plants,
                  "Networth/start:", get_networth(df, money, has_plants, resource) / start_money)

        print()


if __name__ == "__main__":
    main()
