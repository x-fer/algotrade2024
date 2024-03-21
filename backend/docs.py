short_description = """
Docs for Algotrade hackathon - the biggest hackathon in Zagreb.

**FAQ**: In case of any questions, ping organizers in discord or in person!

**IMPORTANT**: Each team will get a team_id. Make sure to send it as a query
parameter in all requests you send!
"""

description = """
Docs for Algotrade hackathon - the biggest hackathon in Zagreb.

## RULES

In this game there is a simulated stock exchange for resources and energy.

Each player is assigned a sum of money at the beggining of the game.

They buy and sell resources on this stoch exchange. Resources 
can be stored in your storage.

Players can also process resources and produce electricity. This 
electricity can also be sold, but cannot be stored.

Player with most money at the end of the round wins!

You create your bots that automatically trade for you and set
produce electricity.


## Games

- One game will be open all night long for testing your bots.

- There will be three competition rounds lasting for 30 minutes. These 
rounds will be scored and they have annotation is_contest=True.

- Before these competition rounds, we will start test rounds that will 
simulate contest. They will also last 30 minutes, but will not be scored.


## Ticks

Game is split into many ticks. In contest rounds one tick equals one
second. In the game that is open all the time a tick equals three seconds.

In one tick players can create new orders and do other requests.

At the end of tick following things happen in this order:

1) Resource orders are added to match engine in time order, and 
then matched on price-time priority.

1) Power plants consume set ammount of resources and then
produces electricity

1) Energy agent buys players energy on price priority

1) If you have energy that is not sold to energy agent, it is destroyed!
So make sure you produce the right amount of energy

Every 5 ticks, our agents create new orders:

1) Resource agents create new resource orders (both buy and sell)

1) Energy agent sets new price and demand for electricity


**FAQ**: In case of any questions, ping organizers in discord or in person!

**IMPORTANT**: Each team will get a team_id. Make sure to send it as a query
parameter in all requests you send!

"""

game_desc = "Here you can see avaliable games."

player_desc = "Manage players in games for your team and get their current info."

market_desc = "Create buy and sell orders for resources, list orders and set price for electricity."

power_plant_desc = "Buy or sell power plants and turn them on or off."

tags_metadata = [
    {
        "name": "Games",
        "description": game_desc,
    },
    {
        "name": "Player",
        "description": player_desc,
    },
    {
        "name": "Market",
        "description": market_desc,
    },
    {
        "name": "Power plants",
        "description": power_plant_desc
    },
]
