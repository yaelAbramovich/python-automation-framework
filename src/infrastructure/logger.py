import logging
from datetime import datetime, timezone
from typing import Optional

from src.config.environment import SupportedLogLevel, environment_configuration

_LOG_FORMAT = "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s"

_LOG_LEVELS: dict[SupportedLogLevel, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}

logging.addLevelName(logging.WARNING, "WARN")


class _UtcFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()


def _configure_root_logger() -> None:
    # Runs exactly once per process: Python caches this module in sys.modules
    # after its first import, so this top-level call never re-executes.
    #
    # Root's own level is left at logging's default (WARNING) rather than
    # widened here — each Logger instance sets its own level explicitly
    # below, so gating for this framework's own loggers never depends on
    # root's level. Widening root would also make third-party libraries
    # that use stdlib logging (e.g. asyncio) print through this handler.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(_UtcFormatter(_LOG_FORMAT))
    root_logger.addHandler(handler)


_configure_root_logger()


class Logger:
    """
    Thin wrapper around Python's standard logging module, keyed by a
    per-caller name (e.g. a page object or API client class name).
    """

    def __init__(self, logger_name: str) -> None:
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(_LOG_LEVELS[environment_configuration.log_level])

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str, cause: Optional[BaseException] = None) -> None:
        if cause is not None:
            self._logger.exception(message, exc_info=cause)
        else:
            self._logger.error(message)
