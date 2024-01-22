

class Bots:
    scripts = {
        "a": "a.py",
        "b": "b.py",
        "c": "c.py",
    }

    def exists(bot_id):
        return bot_id in Bots.scripts

    def validate_string(bot_string):
        bots = bot_string.split(";")
        bots = [bot.split(":") for bot in bots]
        bots = [(bot[0], int(bot[1])) for bot in bots]

        for bot, ammount in bots:
            if not Bots.exists(bot) or ammount < 0 or ammount > 10:
                raise Exception(
                    "Bot does not exist or ammount is not in range [0, 10]")

        return bots
