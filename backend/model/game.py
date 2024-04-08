
from db.db import get_my_redis_connection
from redis_om import  Field, JsonModel
from datetime import datetime


class Game(JsonModel):
    game_name: str
    is_contest: int = Field(index=True)
    dataset_id: str
    start_time: datetime = Field(index=False)
    total_ticks: int
    tick_time: int
    current_tick: int = Field(default=0)
    is_finished: bool = Field(index=False, default=False)

    @property
    def game_id(self) -> str:
        return self.pk

    class Meta:
        database = get_my_redis_connection()