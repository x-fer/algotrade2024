from matplotlib import pyplot as plt
import requests
import yfinance as yf
import pandas as pd

# coal: 3000
# uranium: 250000
# biomass: 5000
# gas: 7000
# oil: 10000
d = {
    'COAL_PRICE': "MTF=F",  # thermal coal
    'URANIUM_PRICE': "PA=F",  # paladium
    'BIOMASS_PRICE': "LBS=F",  # lumber
    'GAS_PRICE': "NG=F",  # natural gas
    'OIL_PRICE': 'CL=F'  # crude oil
}

# all available data
df = yf.download(" ".join(d.values()),
                 period='max')["Adj Close"]

# drop nan on rows
df = df.dropna()

min_date = df.index.min()
max_date = df.index.max()

# interpolate hourly
df = df.resample('H').interpolate()

# print(df)

for col in df.columns:
    # normalize and plot
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    # moving average
    df[col] = df[col].rolling(window=48).mean()

# drop nan on rows
df = df.dropna()

# rename and save to data
df = df.rename(columns={
    v: k for k, v in d.items()
})
df.to_csv('data/futures.csv')

# df.plot()
# plt.show()
