import abc


class Bot():
    def __init__(self, *args, **kwargs):
        self.player_id = 0
        self.game_id = 0

    @abc.abstractmethod
    async def run(self, *args, **kwargs) -> None:
        pass

