import os
import logging
import sys
from logging import FileHandler
from datetime import datetime

PRODUCTION = os.getenv("PRODUCTION", "False") == "True"

logger = logging.getLogger("lucy")
logger.setLevel(logging.WARNING if PRODUCTION else logging.DEBUG)

console_format = logging.Formatter(
    "[%(levelname)s] %(message)s" if PRODUCTION else
    "[%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"
)
file_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s" if PRODUCTION else
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING if PRODUCTION else logging.INFO)
console_handler.setFormatter(console_format)

MB = 1048576

class DateRotatingFileHandler(FileHandler):
    def __init__(self, filename, maxBytes=MB, encoding = None):
        super().__init__(filename, encoding = encoding)
        self.maxBytes = maxBytes

    def shouldRollover(self):
        if os.path.exists(self.baseFilename):
            if os.path.getsize(self.baseFilename) >= self.maxBytes:
                return True
        return False

    def doRollover(self):
        self.close()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_name = os.path.join(
            os.path.dirname(self.baseFilename),
            f"lucy-{timestamp}.log"
        )
        os.rename(self.baseFilename, new_name)
        self.stream = self._open()

    def emit(self, record):
        if self.shouldRollover():
            self.doRollover()
        super().emit(record)

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.abspath(os.path.join(log_dir, "lucy-current.log"))
file_handler = DateRotatingFileHandler(log_path, maxBytes=MB, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_format)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
else:
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
