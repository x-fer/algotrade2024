import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv('data-1710693841401.csv')

df[df["resource"] == "COAL"]["market"].plot()
plt.show()
