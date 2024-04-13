import logging
import logging.handlers
from operator import attrgetter
import types
from typing import List, Tuple
from config import config

logger = logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    '[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s')
console_formatter = logging.Formatter('%(levelname)s:     %(message)s')

console_handler = logging.StreamHandler()

if config['log_level']:
    try:
        console_handler.setLevel(attrgetter(config['log_level'], logging))
    except Exception:
        print("Invalid log level, setting log level to info")
        console_handler.setLevel(logging.INFO)
else:
    console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

file_handler = logging.handlers.RotatingFileHandler('logfile.log', 'a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

class GameLogger(logging.Logger):
    def game_log(self, game_id: str, msg: object, *args, **kwargs):
        self.info(f"      {game_id} {msg}", *args, **kwargs)

logger.game_log = types.MethodType(GameLogger.game_log, logger)
logger: GameLogger


def get_player_text(x):
    player_id, score = x
    return f"({player_id}, {score})"

class ScoreLogger:
    def log(self, game_id: str, game_name: str, tick: int | str, scores: List[Tuple[str, int]]):
        file_name = f"scores/{game_id}_{game_name}.txt"
        try:
            with open(file_name, "a+", encoding="utf8") as file:
                text = ', '.join(map(get_player_text, scores))
                file.write(f"{tick}, [{text}]\n")
        except Exception as e:
            logger.warning(f"Error writing score to file {file_name} for tick {tick}", e)

score_logger = ScoreLogger()