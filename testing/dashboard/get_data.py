import requests
import pandas as pd
from algotrade_api import AlgotradeApi, Resource
import threading
import time

url = "localhost:3000"
team_secret = "gogi"
game_id = 1

api = AlgotradeApi(url, team_secret, game_id)
prices = api.get_prices(start_tick=-100, end_tick=-1).json()

bot_orders = api.get_orders(restriction="bot").json()


def get_market_data():
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

def get_order_data():
    l = []
    data = pd.read_csv('orders.csv')
    for resource in Resource:
        res_data = data[data["resource"] == resource.value]
        l.append({
            "x": res_data["tick"],
            "y": res_data["price"],
            "name": resource.value
        })
    return l


def worker():
    cnt = 0
    while True:
        orders = api.get_orders().json()
        game = api.get_game().json()

        dfs = []
        for resource in Resource:
            df = pd.DataFrame(orders[resource.value])
            df["resource"] = resource.value
            df["tick"] = game["current_tick"]
            dfs.append(df)
        df = pd.concat(dfs)
        # print(df)
        if cnt == 0:
            df.to_csv('orders.csv', mode='w', index=False, header=True)
        else:
            df.to_csv('orders.csv', mode='a', index=False, header=False)
        cnt = 1
        time.sleep(1)
    

thread = threading.Thread(target=worker)
thread.start()