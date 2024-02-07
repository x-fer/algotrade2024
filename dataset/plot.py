import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv("data/out.csv")

# Date as index
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date")

# drop NaN


# plot columns

for col in df.columns:
    df[col].plot()
    plt.title(col)
    plt.show()
