import time
from logger import logger


level = 0


class Timer:    
    def __init__(self, description=None):
        self.description = description

    def __enter__(self):
        global level
        self.start = time.time()
        level += 1
        return self

    def __exit__(self, *args):
        global level
        self.end = time.time()
        self.interval = self.end - self.start
        level -= 1
        if self.description and self.interval > 0.005:
            logger.info(f"{'  '*level:<s}{self.description:} {self.interval:.7f} sec")