import logging
import logging.handlers
from operator import attrgetter
import types
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
# logger.addHandler(file_handler)

class GameLogger(logging.Logger):
    def game_log(self, game_id: str, msg: object, *args, **kwargs):
        self.info(f"      {game_id} {msg}", *args, **kwargs)

logger.game_log = types.MethodType(GameLogger.game_log, logger)
logger: GameLogger