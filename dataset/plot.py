import pandas as pd
from matplotlib import pyplot as plt
import sys

df = pd.read_csv(sys.argv[1])

# Date as index
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

# drop NaN


# plot columns

for col in df.columns:
    df[col].plot()
    plt.title(col)
    plt.show()
