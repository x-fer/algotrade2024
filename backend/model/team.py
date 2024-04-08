from db.db import get_my_redis_connection
from redis_om import Field, JsonModel


class Team(JsonModel):
    team_name: str = Field(index=True)
    team_secret: str = Field(index=True)

    @property
    def team_id(self) -> str:
        return self.pk

    class Meta:
        database = get_my_redis_connection()