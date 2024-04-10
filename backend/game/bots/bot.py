import abc


class Bot():
    def __init__(self, *args, **kwargs):
        self.player_id = None
        self.game_id = None

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> None:
        pass

