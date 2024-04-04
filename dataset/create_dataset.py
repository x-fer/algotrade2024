from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os


# load weather data
l = []
for x in os.listdir("data"):
    if not x.endswith(".csv"):
        continue
    if not x.startswith("1064020"):
        continue

    df = pd.read_csv(f"data/{x}", skiprows=2)
    l.append(df)
df = pd.concat(l)

df["Date"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
df = df.set_index("Date")
df = df.drop(columns=["Year", "Month", "Day", "Hour", "Minute"])
df = df.rename(columns={"Global Horizontal UV Irradiance (280-400nm)": "UV"})
df = df.rename(columns={"Precipitable Water": "Rain"})
df = df.rename(columns={"Wind Speed": "Wind"})
df = df.rename(columns={"Temperature": "Temp"})


# load energy data
energy = pd.read_csv("data/DUQ_hourly.csv")
energy["Datetime"] = pd.to_datetime(energy["Datetime"])
energy = energy.set_index("Datetime")
energy = energy.rename(columns={"DUQ_MW": "Energy"})
energy.index = energy.index + pd.Timedelta("30 minutes")

df = df.merge(energy, left_index=True, right_index=True)

df = df[["Temp", "Rain", "Wind", "UV", "Energy"]]

df = df.dropna()


# load river data
river = pd.read_csv("data/river.csv")
river["date"] = pd.to_datetime(river["date"])
river = river.set_index("date")
river = river.drop(columns=["status"])
river = river.rename(columns={"river_level": "River"})

df = df.merge(river, left_index=True, right_index=True)

df = df.dropna()


# load market data
futures_df = pd.read_csv("data/futures.csv", index_col=0)
futures_df.index = pd.to_datetime(futures_df.index) + pd.Timedelta("30 minutes")
# futures_df.rolling(3).mean()

df = df.join(futures_df)

df = df.dropna()


# split data where time jumps
time_delta = df.index[1:] - df.index[:-1]
df = df.iloc[1:]
df["delta"] = time_delta
# split where delta is not 60 minutes
df["split"] = df["delta"] != pd.Timedelta("60 minutes")
# cumsum split
df["split"] = df["split"].cumsum()
# group by split
groups = df.groupby("split")


# Prepare data for csv -> these go directly to game and sql
def prepare_chunk(df: pd.DataFrame) -> pd.DataFrame:
    def mavg_noise(box_size, size):
        noise = np.random.normal(0, 1, size + box_size - 1)
        return np.convolve(np.ones(box_size) / box_size, noise, mode="valid")

    def norm_col(col):
        return col / col[:1800].mean()

    def add_linear(col):
        end = 0.12 * len(col) / 1800
        col = 0.4 + col + np.linspace(0, end, len(col))
        return norm_col(col)

    # scale so all cols average to 1
    df = df * (1 / df.mean())

    new_df = pd.DataFrame(
        columns=[
            "date",
            "COAL",
            "URANIUM",
            "BIOMASS",
            "GAS",
            "OIL",
            "GEOTHERMAL",
            "WIND",
            "SOLAR",
            "HYDRO",
            "ENERGY_DEMAND",
            "MAX_ENERGY_PRICE",
        ]
    )
    new_df["date"] = df.index.to_series()

    new_df["COAL"] = mavg_noise(24, len(df)) * 0.02
    new_df["URANIUM"] = mavg_noise(24, len(df)) * 0.02
    new_df["BIOMASS"] = mavg_noise(24, len(df)) * 0.02
    new_df["GAS"] = mavg_noise(24, len(df)) * 0.02
    new_df["OIL"] = mavg_noise(24, len(df)) * 0.02

    new_df["GEOTHERMAL"] = df["Rain"]
    new_df["WIND"] = df["Wind"]
    new_df["SOLAR"] = df["UV"]
    new_df["HYDRO"] = df["River"]

    new_df["ENERGY_DEMAND"] = df["Energy"]
    new_df["MAX_ENERGY_PRICE"] = norm_col(
        0.3 + 0.6 * 1 / df["Energy"] + 0.1 * 1 / df["Energy"] ** 2
    )

    new_df["COAL_PRICE"] = add_linear(df["COAL_PRICE"])
    new_df["URANIUM_PRICE"] = add_linear(df["URANIUM_PRICE"])
    new_df["BIOMASS_PRICE"] = add_linear(df["BIOMASS_PRICE"])
    new_df["GAS_PRICE"] = add_linear(df["GAS_PRICE"])
    new_df["OIL_PRICE"] = add_linear(df["OIL_PRICE"])

    for col in new_df.columns:
        # make int
        if col == "date":
            continue
        new_df[col] *= 1_000_000
        new_df[col] = new_df[col].apply(lambda x: int(x))
        new_df[col] = new_df[col].astype(int)

    l = []
    for col in new_df.columns:
        if col == "date":
            continue

        # plt.plot(new_df[col], label=col)
        l.append(new_df[col].sum())

    # plt.title("Dataset outputs")
    # plt.legend()
    # plt.show()

    # plt.bar(new_df.columns[1:], l)
    # plt.title("Dataset outputs sum")
    # plt.legend()
    # plt.show()
    graph_df = new_df.iloc[:1800:3, :]
    plt.plot(graph_df["COAL_PRICE"], label="COAL")
    plt.plot(graph_df["URANIUM_PRICE"], label="URANIUM")
    plt.plot(graph_df["BIOMASS_PRICE"], label="BIO")
    plt.plot(graph_df["GAS_PRICE"], label="GAS")
    plt.plot(graph_df["OIL_PRICE"], label="OIL")
    plt.legend()
    plt.show() 

    # plt.plot(new_df["ENERGY_DEMAND"][:1800])
    # plt.plot(new_df["MAX_ENERGY_PRICE"])
    # plt.title("PRICES")
    # plt.show() 

    return new_df


for name, group in groups:
    # save to chunks

    if len(group) < 2000:
        continue

    # drop split and delta
    group = group.drop(columns=["split", "delta"])

    # assert that time delta is 60 minutes
    time_delta = group.index[1:] - group.index[:-1]

    assert all(time_delta == pd.Timedelta("60 minutes"))

    group = prepare_chunk(group)

    group.to_csv(
        f"chunks/df_{len(group)}_{group.index[0]}_{group.index[-1]}.csv", index=False
    )
