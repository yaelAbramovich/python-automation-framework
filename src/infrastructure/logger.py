from datetime import datetime, timezone

from src.config.environment import SupportedLogLevel, environment_configuration

_LOG_LEVEL_SEVERITY_ORDER: dict[str, int] = {
    "debug": 10,
    "info": 20,
    "warn": 30,
    "error": 40,
}


def _should_log_at_level(message_level: SupportedLogLevel) -> bool:
    configured_severity = _LOG_LEVEL_SEVERITY_ORDER[environment_configuration.log_level]
    message_severity = _LOG_LEVEL_SEVERITY_ORDER[message_level]
    return message_severity >= configured_severity


def _build_formatted_log_line(logger_name: str, level: SupportedLogLevel, message: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    level_label = level.upper().ljust(5)
    return f"[{timestamp}] [{level_label}] [{logger_name}] {message}"


class Logger:
    def __init__(self, logger_name: str) -> None:
        self._logger_name = logger_name

    def debug(self, message: str) -> None:
        if _should_log_at_level("debug"):
            print(_build_formatted_log_line(self._logger_name, "debug", message))

    def info(self, message: str) -> None:
        if _should_log_at_level("info"):
            print(_build_formatted_log_line(self._logger_name, "info", message))

    def warn(self, message: str) -> None:
        if _should_log_at_level("warn"):
            print(_build_formatted_log_line(self._logger_name, "warn", message))

    def error(self, message: str, cause: object = None) -> None:
        if not _should_log_at_level("error"):
            return
        print(_build_formatted_log_line(self._logger_name, "error", message))
        if cause is not None:
            print(cause)
