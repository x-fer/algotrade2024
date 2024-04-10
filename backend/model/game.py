
from typing import Any, Optional
from db.db import get_my_redis_connection
from redis_om import  Field, JsonModel
from datetime import datetime


class Game(JsonModel):
    game_name: str
    is_contest: int = Field(index=True)
    dataset_id: str
    start_time: datetime = Field(index=False, sortable=True)
    total_ticks: int
    tick_time: int
    current_tick: int = Field(default=0)
    is_finished: bool = Field(index=False, default=False)

    game_id: str = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.game_id=self.pk

    class Meta:
        database = get_my_redis_connection()
