import datetime
import requests
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback
from .get_data import get_order_data
import plotly

# https://realpython.com/python-dash/


external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "dashboard"



@callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'), 
              Input('live-update-graph', 'figure'))
def update_data(n, fig):
    
    # fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    # fig["data"] = ,
    fig["data"] = get_order_data() 
    return fig


app.layout = html.Div(
    children=[
        html.H1(children="Price analytics", className="header-title"),
        html.P(
            children=(
                "Analyze the behavior of algotrade resource prices on market in last 100 ticks."
            ),
            className="header-description",
        ),
        dcc.Graph(
            id='live-update-graph',
            figure={
                "data": None,
                "layout": {"title": "Market Price of Resources"},
            },
        ),
        dcc.Interval(
            id='interval-component',
            interval=1000, # in milliseconds
            n_intervals=0
        ),
    ],
    className="header",
)

if __name__ == "__main__":
    app.run_server(debug=True)