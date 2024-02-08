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

for name, group in groups:
    # save to chunks

    # drop split and delta
    group = group.drop(columns=["split", "delta"])

    # assert that time delta is 60 minutes
    time_delta = group.index[1:] - group.index[:-1]

    assert all(time_delta == pd.Timedelta("60 minutes"))

    group.to_csv(
        f"chunks/df_{len(group)}_{group.index[0]}_{group.index[-1]}.csv")

# print(df)

# Save
# df.to_csv("data/out.csv")

# print(df)
