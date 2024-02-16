from matplotlib import pyplot as plt
import pandas as pd
import os

# list data/ dir
l = []
for x in os.listdir("data"):
    if not x.endswith(".csv"):
        continue
    if not x.startswith("1064020"):
        continue

    # ignore first 2 rows
    df = pd.read_csv(f"data/{x}", skiprows=2)

    l.append(df)

df = pd.concat(l)

# Year,Month,Day,Hour,Minute to date and index
df["Date"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
df = df.set_index("Date")

# drop columns
df = df.drop(columns=["Year", "Month", "Day", "Hour", "Minute"])

energy = pd.read_csv("data/DUQ_hourly.csv")

# Datetime to date and index
energy["Datetime"] = pd.to_datetime(energy["Datetime"])
energy = energy.set_index("Datetime")

# add 30:00 to all dates
energy.index = energy.index + pd.Timedelta("30 minutes")

# print(energy)

# print(df)

# Merge on index
df = df.merge(energy, left_index=True, right_index=True)

# Drop NaN
df = df.dropna()

# leave Date,Temperature,Precipitable Water,Wind Speed,Global Horizontal UV Irradiance (280-400nm)
df = df[["Temperature", "Precipitable Water",
         "Wind Speed", "Global Horizontal UV Irradiance (280-400nm)", "DUQ_MW"]]

# Rename columns
df = df.rename(columns={"Global Horizontal UV Irradiance (280-400nm)": "UV"})
df = df.rename(columns={"Precipitable Water": "Rain"})
df = df.rename(columns={"Wind Speed": "Wind"})
df = df.rename(columns={"Temperature": "Temp"})
df = df.rename(columns={"DUQ_MW": "Energy"})

# Drop NaN
df = df.dropna()


# load river data

river = pd.read_csv("data/river.csv")
# set date as index
river["date"] = pd.to_datetime(river["date"])
river = river.set_index("date")

# merge on index
df = df.merge(river, left_index=True, right_index=True)

# drop status
df = df.drop(columns=["status"])

# rename river_level to river
df = df.rename(columns={"river_level": "River"})

df = df.dropna()

# assert time delta is 60 minutes


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

# await database.execute('''
#                 CREATE TABLE IF NOT EXISTS dataset_data (
#                 dataset_data_id SERIAL PRIMARY KEY,
#                 dataset_id INT NOT NULL,
#                 date TIMESTAMP NOT NULL,
#                 COAL INT NOT NULL,
#                 URANIUM INT NOT NULL,
#                 BIOMASS INT NOT NULL,
#                 GAS INT NOT NULL,
#                 OIL INT NOT NULL,
#                 GEOTHERMAL INT NOT NULL,
#                 WIND INT NOT NULL,
#                 SOLAR INT NOT NULL,
#                 HYDRO INT NOT NULL,
#                 ENERGY_DEMAND INT NOT NULL,
#                 MAX_ENERGY_PRICE INT NOT NULL,
#                 FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
#                 )''')


def prepare_chunk(df):

    # scale to 0 1
    df = (df - df.min()) / (df.max() - df.min())

    new_df = pd.DataFrame(columns=["date", "COAL", "URANIUM", "BIOMASS", "GAS", "OIL",
                                   "GEOTHERMAL", "WIND", "SOLAR", "HYDRO", "ENERGY_DEMAND", "MAX_ENERGY_PRICE"])

    new_df["date"] = df.index.to_series()

    # all in kW
    # COAL:

    new_df["COAL"] = 300 * 1000 + 100 * df["Temp"]
    new_df["URANIUM"] = 500 * 1000 + 100 * df["Temp"]
    new_df["BIOMASS"] = 100 * 1000 + 100 * df["Temp"]
    new_df["GAS"] = 200 * 1000 + 100 * df["Temp"]
    new_df["OIL"] = 50 * 1000 + 100 * df["Temp"]

    new_df["GEOTHERMAL"] = 300 * 1000 * df["Rain"]
    new_df["WIND"] = 50 * 1000 * df["Wind"]
    new_df["SOLAR"] = 100 * 1000 * df["UV"]
    new_df["HYDRO"] = 300 * 1000 * df["River"]

    new_df["ENERGY_DEMAND"] = 3000 * 1000 + 5000 * 1000 * df["Energy"]
    new_df["MAX_ENERGY_PRICE"] = 1000 - 500 * df["Energy"]

    for col in new_df.columns:
        # make int
        if col == "date":
            continue
        new_df[col] = new_df[col].apply(lambda x: int(x))
        new_df[col] = new_df[col].astype(int)

    l = []
    for col in new_df.columns:
        if col == "date":
            continue

        plt.plot(new_df[col], label=col)
        l.append(new_df[col].sum())

    # plt.title("Dataset outputs")
    # plt.legend()
    # plt.show()

    # plt.bar(new_df.columns[1:], l)
    # plt.title("Dataset outputs sum")
    # plt.legend()
    # plt.show()

    # plt.plot(new_df["MAX_ENERGY_PRICE"])
    # plt.plot(new_df["ENERGY_DEMAND"].apply(lambda x: x / 10000))
    # plt.title("MAX_ENERGY_PRICE vs DEMAND")
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
        f"chunks/df_{len(group)}_{group.index[0]}_{group.index[-1]}.csv", index=False)
