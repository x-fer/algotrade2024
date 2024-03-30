import requests
import pandas as pd
from dash import Dash, dcc, html
from algotrade_api import AlgotradeApi, Resource

# https://realpython.com/python-dash/

url = "localhost:3000"

team_secret = "gogi"
game_id = 1

api = AlgotradeApi(url, team_secret, game_id)
prices = api.get_prices(start_tick=-100, end_tick=-1).json()

def get_data():
    l = []
    for resource in Resource:
        data = pd.DataFrame(prices[resource.value])
        l.append({
            "x": data["tick"],
            "y": data["market"],
            "type": "lines",
            "hovertemplate": (
                "$%{y:.2f}<extra></extra>"
            ),
        })
    return l




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
            figure={
                "data": get_data(),
                "layout": {"title": "Market Price of Resources"},
            },
        ),
    ],
    className="header",
)

if __name__ == "__main__":
    app.run_server(debug=True)