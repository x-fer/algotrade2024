from datetime import date
import cairosvg
import pandas as pd
import pygal
from pygal.style import Style

df = pd.read_csv('sample.csv')

line_chart_config = Style(
    background='white',
    plot_background='white',
    foreground='black',
    foreground_strong='black',
    foreground_subtle='black',
    opacity='.6',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53')
)

line_chart = pygal.XY(style=line_chart_config, xrange=(1, 600))
line_chart.title = 'Solar power plant electricity output'

df = df.head(600).copy()
df['SOLAR'] *= 35/1000000

line_chart.x_title = 'tick'
line_chart.y_title = 'electricity output'

line_chart.add('SOLAR', list(zip(df.index.to_list(), df['SOLAR'].to_list())))

line_chart.render_to_file('solar.svg')
cairosvg.svg2svg(url='solar.svg', write_to='solar.svg')
