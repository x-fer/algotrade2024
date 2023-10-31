from subprocess import Popen, PIPE
from multiprocessing import Process
import uvicorn

import json
from game.game import run


def main():
    # run redis server

    config = json.load(open("../config/config.json"))

    redis_server = Popen(
        ["redis-server", "--port", str(config["redis"]["port"])], stdout=PIPE)

    # run games for test

    games = []

    for id in range(3):
        games.append(Process(target=run, args=(id, f"game_{id}", 0, 0)))

    for game in games:
        game.start()

    # run server

    uvicorn.run("server.server:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
