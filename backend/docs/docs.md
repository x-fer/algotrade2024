
# Algotrade hackathon

Algotrade hackathon game rules and technical details.

## Table of contents
1. [Task description](#task)
    1. [Resource market](#resource_market)
    1. [Power plants](#resource_market)
    1. [Electricity market](#resource_market)
1. [Ticks](#ticks)
1. [Rounds and scoring](#games)

## Task description <a name="task"></a>

There is a simulated stock exchange for resources and energy.
At the beggining of a game you are given a sum of money. 
You can buy and sell your resources on *resource market*.
Resources can be stored in your storage.

You can also process resources you own and produce electricity using *power plants*. This electricity can be sold on *electricity market*, but cannot be stored.

Player with the most money at the end of the game wins!

<img src="./trzista.drawio.svg" style="width:450px;height:300px;">



## Resource market <a name="resource_market"></a>

There are 5 types of resources in this game. These are **coal, uranium, biomass, gas and oil**. They all have different power outputs and different prices for respective power plants.
Users can buy and sell resources using *orders*.

Game is split into [ticks](#ticks). During ticks you place your orders which will be put in the order matching engine at the end of the tick.

Order is defined by:
- order side: BUY / SELL
- resource: resource you want to buy or sell
- order size: number of resources you are trading
- order price: price per unit of resource you are selling (not the total price of the order)
- expiration tick: tick in the game when this order expires

### Matching engine

will place the orders by the time of arrival - as if they were evaluated real time. They are evalueated at the end of the tick for performance reasons. 

- If the order is BUY order: engine will look for the SELL order with the lowest price that is already in the engine and if the price is lower than the price of the BUY order, they will match. 
- If the order is SELL order: engine will look for the BUY order with the highest price that is already in the engine and if the price is lower than the price of the BUY order, they will match.

If during this process there are two orders with the same price, engine will look for the first one. If no matching order is found, placed order will be saved by engine for later matching, until it expires.

When orders match, price of the first order is set as trade price. Then the engine checks if the selling player has enough resources and if buying player has enough money. If not, the respective order is cancelled. Otherwise, both order sizes are reduced until one of them is filled. One that is not filled is matched again.

### Matching example

The table below is showing already placed orders for coal resource.

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | $250 | 400 |
|2| SELL | $260 | 300 |
|3| SELL | $290 | 300 |

Now three new orders arrive in this order:
[
(4, BUY, $270, 400),
(5, BUY, $280, 100),
(6, SELL, $220, 100)
]
During the tick, they are saved to queue. At the end of the tick, orders are matched:

First order in queue (order 4) is matched with order 2. Trade price is set to $260 and size to 300. Order 2 is filled, and player who placed order 4 will pay 300 x $260 = $18,000. However order 4 is still not filled. Now it matches again, but all orders are too high, so it is saved by the engine. Table now looks like:

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | $250 | 400 |
|4| BUY | $270 | 100 |
|3| SELL | $290 | 300 |

Order 5 is now matched, but all SELL orders are too expensive. It is also saved by engine.


| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | $250 | 400 |
|4| BUY | $270 | 100 |
|5| BUY | $280 | 100 |
|3| SELL | $290 | 300 |

Order 6 is matched with order 5 with price $280 and size 100. Both orders 5 and 6 are filled. Player who placed order 5 pays $280 x 100 = $28,000, and player 6 pays 100 oil resources. In the end the table looks like this:

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | $250 | 400 |
|4| BUY | $270 | 100 |
|3| SELL | $290 | 300 |

### Bot orders

Our bots place orders on the market. They are supposed to controll the market

## Ticks <a name="ticks"></a>

Game is split into many ticks.
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









## Technical details <a name="games"></a>

- One game will be open all night long for testing your bots.

- There will be three competition rounds lasting for 30 minutes. These 
rounds will be scored and they have annotation is_contest=True.

- Before these competition rounds, we will start test rounds that will 
simulate contest. They will also last 30 minutes, but will not be scored.
