import logging
import logging.handlers

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s')
console_formatter = logging.Formatter('%(levelname)s:     %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

file_handler = logging.handlers.RotatingFileHandler('logfile.log', 'a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
