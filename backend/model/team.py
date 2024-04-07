from redis_om import Field, HashModel, get_redis_connection


class Team(HashModel):
    team_name: str
    team_secret: str = Field(index=True)

    @property
    def team_id(self) -> str:
        return self.pk

    class Meta:
        database = get_redis_connection(port=6479)