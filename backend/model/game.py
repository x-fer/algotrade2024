
from redis_om import  Field, JsonModel, get_redis_connection
from datetime import datetime


class Game(JsonModel):
    game_name: str
    is_contest: bool
    dataset_id: str
    start_time: datetime
    total_ticks: int
    tick_time: int
    current_tick: int = Field(index=False, default=0)
    is_finished: bool = Field(index=False, default=False)

    @property
    def game_id(self) -> str:
        return self.pk

    class Meta:
        database = get_redis_connection(port=6479)