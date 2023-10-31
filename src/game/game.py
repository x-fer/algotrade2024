import redis
import time


def run(*args, **kwargs):
    game = Game(*args, **kwargs)
    game.run()


class Game():
    def __init__(self, id, name, created_at, start_at, tick_interval=1):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.start_at = start_at
        self.players = []
        self.tick_interval = tick_interval

        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def __repr__(self):
        return "<Game(name='%s', created_at='%s')>" % (
            self.name, self.created_at)

    def do_action(self, action):
        # player logic
        print(action)

    def default_tick_action(self):
        # game logic
        print("tick")

    def tick(self):
        messages_len = self.redis.llen(f"game_{self.id}")

        for _ in range(messages_len):
            message = self.redis.lpop(f"game_{self.id}")
            self.do_action(message)

        self.default_tick_action()

    def run(self):

        while True:
            start = time.time()
            self.tick()
            end = time.time()

            print(f"tick took {end - start} seconds")

            if end - start >= self.tick_interval:
                print("[W] tick took too long")

            time.sleep(max(0, self.tick_interval - (end - start)))
