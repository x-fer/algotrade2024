from datetime import date
import cairosvg
import pandas as pd
import pygal
from pygal.style import Style

df = pd.read_csv('sample.csv')

# transparent background white lines and text
line_chart_config = Style(
    background='transparent',
    plot_background='transparent',
    foreground='white',
    foreground_strong='white',
    foreground_subtle='white',
    opacity='.6',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53')
)


line_chart = pygal.DateLine(x_label_rotation=45, style=line_chart_config)
line_chart.title = 'Energy price in $ per kW/h'

# resample to 100 data points
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')


# date,COAL,URANIUM,BIOMASS,GAS,OIL,GEOTHERMAL,WIND,SOLAR,HYDRO,ENERGY_DEMAND,MAX_ENERGY_PRICE
line_chart.x_labels = df.index.to_series().resample('5D').mean().map(
    lambda d: date(d.year, d.month, d.day))

line_chart.add('MAX_ENERGY_PRICE', list(
    zip(map(lambda d: date(d.year, d.month, d.day), df.index.to_series().tolist()
            ), df['MAX_ENERGY_PRICE'].tolist())))


line_chart.render_to_file('line_chart.svg')

cairosvg.svg2svg(url='line_chart.svg', write_to='line_chart.svg')
