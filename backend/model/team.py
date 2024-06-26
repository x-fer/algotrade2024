from db.db import get_my_redis_connection
from redis_om import Field, JsonModel
from redlock.lock import RedLock


class Team(JsonModel):
    team_name: str = Field(index=True)
    team_secret: str = Field(index=True)
    team_id: str = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.team_id = self.pk

    def lock(self, *args):
        return RedLock(self.pk, *args)

    class Meta:
        database = get_my_redis_connection()
