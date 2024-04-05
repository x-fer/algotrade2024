import logging
import logging.handlers
from config import config

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    '[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s')
console_formatter = logging.Formatter('%(levelname)s:     %(message)s')

console_handler = logging.StreamHandler()

if config['debug']:
    console_handler.setLevel(logging.DEBUG)
else:
    console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

file_handler = logging.handlers.RotatingFileHandler('logfile.log', 'a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

real_logger = logger

from timer import Timer
from time import time

class Logger():
    def __init__(self):
        self.log_interval = 0
        self.start = None
    
    def end(self):
        if self.start is not None:
            tick_time = time() - self.start
            # real_logger.info(f"Logging took {self.log_interval/tick_time:.2%} = {self.log_interval:.4f}/{tick_time:.4f}sec")
        self.start = time()
        self.log_interval = 0

    def info(self, *args, **kwargs):
        with Timer() as t:
            real_logger.info(*args, **kwargs)
        self.log_interval += t.interval

    def warning(self, *args, **kwargs):
        with Timer() as t:
            real_logger.warning(*args, **kwargs)
        self.log_interval += t.interval

    def debug(self, *args, **kwargs):
        with Timer() as t:
            real_logger.debug(*args, **kwargs)
        self.log_interval += t.interval

    def critical(self, *args, **kwargs):
        with Timer() as t:
            real_logger.critical(*args, **kwargs)
        self.log_interval += t.interval

logger = Logger()