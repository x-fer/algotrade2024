from fastapi import HTTPException
from typing import List, Tuple

from .bot import Bot
from .dummy import DummyBot
from .resource_bot import ResourceBot


class Bots:
    bots = {
        "dummy": DummyBot,
        "resource_bot": ResourceBot
    }

    def exists(bot_id):
        return bot_id in Bots.bots

    def parse_string(bot_string: str) -> List[Tuple[str, int]]:
        if bot_string == "":
            return []

        try:
            bots = bot_string.split(";")
            bots = [bot.replace(" ", "") for bot in bots]
            bots = [bot.split(":") for bot in bots]
            bots = [(bot[0], int(bot[1])) for bot in bots]
        except:
            raise HTTPException(400,
                                "Bot string in invalid format, expected: \"[bot_name]:[bot_ammount];\"")

        for bot, ammount in bots:
            if not Bots.exists(bot):
                raise HTTPException(400,
                                    "Bot does not exist")
            if ammount < 0 or ammount > 10:
                raise HTTPException(400,
                                    "Bot ammount is not in range [0, 10]")

        return bots

    def create_bots(bot_string: str, *args, **kwargs) -> List[Bot]:

        bots = Bots.parse_string(bot_string)
        return [
            Bots.bots[bot_name](*args, **kwargs)
            for bot_name, ammount in bots
            for _ in range(ammount)
        ]
