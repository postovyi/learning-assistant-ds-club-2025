import sys

from loguru import logger as loguru_logger


class AppLogger:
    def __init__(self):
        loguru_logger.remove(0)
        loguru_logger.add(sys.stderr)
        self._logger = loguru_logger

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)


logger = AppLogger()