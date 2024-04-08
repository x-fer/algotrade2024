from dataclasses import dataclass
from model.enum_type import get_enum
from .resource import Resource, Energy

market_id = 0
market_db = {}


@dataclass
class Market:
    table_name = "market"
    market_id: int
    game_id: int
    tick: int
    resource: Resource | Energy
    low: int
    high: int
    open: int
    close: int
    market: int
    volume: int

    def __post_init__(self):
        self.resource = get_enum(self.resource, Resource, Energy)

    @classmethod
    async def create(cls, *args, **kwargs) -> int:
        global market_id, market_db

        market_id += 1
        market = Market(market_id=market_id, *args, **kwargs)

        market_db[market_id] = market

        return market_id

    @classmethod
    async def list_by_game_id_where_tick(cls, game_id, min_tick, max_tick, resource: Resource | Energy = None):
        # resource_query = "" if resource is None else " AND resource=:resource"
        # query = f"""
        # SELECT * FROM {cls.table_name}
        # WHERE game_id=:game_id AND tick BETWEEN :min_tick AND :max_tick{resource_query}
        # ORDER BY tick
        # """
        # values = {"game_id": game_id,
        #           "min_tick": min_tick,
        #           "max_tick": max_tick}
        # if resource is not None:
        #     values["resource"] = resource.value
        # result = await database.fetch_all(query, values)
        # return [cls(**game) for game in result]

        global market_db, market_id

        return [market for market in market_db.values() if
                market.game_id == game_id and
                min_tick <= market.tick <= max_tick and
                (resource is None or market.resource == resource)]
