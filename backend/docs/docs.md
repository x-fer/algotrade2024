
# Algotrade hackathon

Docs for Algotrade hackathon - the biggest hackathon in Zagreb.

## Table of contents
1. [Task description](#task)
1. [Games](#games)
1. [Ticks](#ticks)

## Task description <a name="task"></a>

There is a simulated stock exchange for resources and energy.
At the beggining of a game you are given a sum of money. 
With money you can buy and sell your resources on resource market.
Resources can be stored in your storage.

Beyond that, you can also process resources you own and produce electricity. This electricity can be sold on electricity market, but cannot be stored.

Player with the most money at the end of the game wins!


<img src="./trzista.drawio.svg" style="width:450px;height:300px;">

## Technical details <a name="games"></a>

- One game will be open all night long for testing your bots.

- There will be three competition rounds lasting for 30 minutes. These 
rounds will be scored and they have annotation is_contest=True.

- Before these competition rounds, we will start test rounds that will 
simulate contest. They will also last 30 minutes, but will not be scored.


## Ticks <a name="ticks"></a>

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
