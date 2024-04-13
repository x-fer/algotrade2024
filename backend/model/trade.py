from typing import Optional
from redis_om import JsonModel, Field

from db.db import get_my_redis_connection
from model.order import Order
from model.resource import ResourceOrEnergy


class Trade(JsonModel):
    tick: int = Field(index=True)

    total_price: int
    trade_size: int
    trade_price: int

    resource: ResourceOrEnergy = Field(index=True, default="energy")
    game_id: str = Field(index=True, default="game")
    buy_order_id: str = Field(index=True, default="0")
    sell_order_id: str = Field(index=True, default="0")

    buy_player_id: str = Field(index=True, default="0")
    sell_player_id: str = Field(index=True, default="0")

    def __setattr__(self, name, value):
        if name == "buy_order":
            self.resource = value.resource
            self.buy_order_id = value.pk
            self.buy_player_id = value.player_id
            self.game_id = value.game_id
        elif name == "sell_order":
            self.resource = value.resource
            self.sell_order_id = value.pk
            self.sell_player_id = value.player_id
            self.game_id = value.game_id
        return super().__setattr__(name, value)

    class Meta:
        database = get_my_redis_connection()