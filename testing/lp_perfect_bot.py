
import pandas as pd
import gurobipy as gp

df = pd.read_csv(
    '../backend/data/df_2431_2011-11-06 03:30:00_2012-02-15 09:30:00.csv')


price_multiplier = {
    "coal": 2400,
    "uranium": 30000,
    "biomass": 6000,
    "gas": 6070,
    "oil": 6000,
    "energy": 50
}


energy_output_multiplier = {
    "coal": 150,
    "uranium": 1600,
    "biomass": 300,
    "gas": 300,
    "oil": 300,
    "geothermal": 30,
    "wind": 10,
    "solar": 10,
    "hydro": 20
}

energy_demand_multiplier = 30000

coal_base = 302500


def next_price(has):
    global coal_base

    return int(coal_base * (1 + 0.5 * has))


def main():
    model = gp.Model("PerfectBot")

    bought_coal = [
        model.addVar(vtype=gp.GRB.INTEGER, name="bought_coal_{}".format(i))
        for i in range(len(df))
    ]
    bought_plant = [
        model.addVar(vtype=gp.GRB.INTEGER, name="bought_plant_{}".format(i))
        for i in range(len(df))
    ]

    has_coal = [
        model.addVar(vtype=gp.GRB.INTEGER, name="has_coal_{}".format(i))
        for i in range(len(df))
    ]

    has_plant = [
        model.addVar(vtype=gp.GRB.INTEGER, name="has_plant_{}".format(i))
        for i in range(len(df))
    ]

    has_money = [
        model.addVar(vtype=gp.GRB.INTEGER, name="has_money_{}".format(i))
        for i in range(len(df))
    ]

    for i, x in enumerate(df.to_dict('records')):
        last_has_coal = has_coal[i - 1] if i > 0 else 0
        model.addConstr(has_coal[i] == last_has_coal + bought_coal[i])

        last_has_plant = has_plant[i - 1] if i > 0 else 0
        model.addConstr(has_plant[i] == last_has_plant + bought_plant[i])

        last_has_money = has_money[i - 1] if i > 0 else 0
        model.addConstr(
            has_money[i] == last_has_money - next_price(has_coal[i]))


if __name__ == "__main__":
    main()
