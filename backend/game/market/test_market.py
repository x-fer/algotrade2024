import pandas as pd
from db.model.order_types import OrderSide
from ..orderbook import OrderBook, Trade
from ..price_tracker import PriceTracker
from db.model import Order, Player, Resource, Game
from .market import Market
import pytest


@pytest.fixture
def game_id():
    return 1


@pytest.fixture
def game(game_id):
    return Game(game_id=game_id, 
                game_name=f"game_{game_id}",
                is_contest=False,
                bots="",
                dataset="",
                start_time=pd.Timestamp.now(),
                total_ticks=1000,
                tick_time=1000,
                )


@pytest.fixture
def team_id():
    return 1


@pytest.fixture
def get_player(game_id, team_id):
    player_id = 0
    def get_player(**kwargs) -> Player:
        nonlocal player_id
        player = Player(
            player_id=player_id,
            player_name=f"player_{player_id}",
            team_id=team_id,
            game_id=game_id,
            **kwargs
        )
        player_id += 1
        return player
    return get_player


@pytest.fixture
def get_order(game_id):
    order_id=0
    def get_order(player_id: int, price: int, size: int, order_side: OrderSide) -> Order:
        nonlocal order_id
        order = Order(
            order_id=order_id,
            game_id=game_id,
            player_id=player_id,
            resource=Resource.coal.value,
            price=price,
            size=size,
            order_side=order_side
        )
        order_id += 1
        return order
    return get_order


def get_player_dict(players: list[Player]) -> dict[int, Player]:
    return {player.player_id: player for player in players}


@pytest.fixture
def coal_market():
    return Market(Resource.coal, 1)


class TestMoneyUpdate():
    def test_when_transaction_successful(self, get_player, get_order, coal_market):
        player_1: Player = get_player(money=100, coal=0)
        player_2: Player = get_player(money=0, coal=100)
        order_1 = get_order(player_id=player_1.player_id, price=1, size=100, order_side=OrderSide.BUY)
        order_2 = get_order(player_id=player_2.player_id, price=1, size=100, order_side=OrderSide.SELL)

        coal_market.set_players(get_player_dict([player_1, player_2]))
        coal_market.orderbook.add_order(order_1)
        coal_market.orderbook.add_order(order_2)
        coal_market.orderbook.match(1)

        assert player_1.money == 0
        assert player_1.coal == 100
        assert player_2.money == 100
        assert player_2.coal == 0
        

