
class Game():
    def __init__(self, id, name, created_at, start_at):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.start_at = start_at
        self.players = []

    def __repr__(self):
        return "<Game(name='%s', created_at='%s')>" % (
            self.name, self.created_at)
