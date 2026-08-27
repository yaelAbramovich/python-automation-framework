import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, cast, get_args

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path.cwd() / ".env")

SupportedLogLevel = Literal["debug", "info", "warn", "error"]
_SUPPORTED_LOG_LEVELS = get_args(SupportedLogLevel)


def _read_environment_variable_or_none(variable_name: str) -> Optional[str]:
    raw_value = os.environ.get(variable_name)
    if raw_value is None or raw_value.strip() == "":
        return None
    return raw_value.strip()


def _read_string_environment_variable_or_default(variable_name: str, default_value: str) -> str:
    return _read_environment_variable_or_none(variable_name) or default_value


def _read_int_environment_variable_or_default(variable_name: str, default_value: int) -> int:
    raw_value = _read_environment_variable_or_none(variable_name)
    if raw_value is None:
        return default_value
    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(
            f'Environment variable "{variable_name}" must be an integer but got "{raw_value}"'
        ) from error


def _read_log_level_environment_variable_or_default(
    variable_name: str, default_value: SupportedLogLevel
) -> SupportedLogLevel:
    raw_value = _read_environment_variable_or_none(variable_name)
    if raw_value is None:
        return default_value
    normalized_value = raw_value.lower()
    if normalized_value not in _SUPPORTED_LOG_LEVELS:
        raise ValueError(
            f'Environment variable "{variable_name}" must be one of '
            f'{_SUPPORTED_LOG_LEVELS} but got "{raw_value}"'
        )
    return cast(SupportedLogLevel, normalized_value)


@dataclass(frozen=True)
class EnvironmentConfiguration:
    ui_base_url: str
    api_base_url: str
    default_action_timeout_ms: int
    default_navigation_timeout_ms: int
    log_level: SupportedLogLevel


environment_configuration = EnvironmentConfiguration(
    ui_base_url=_read_string_environment_variable_or_default(
        "UI_BASE_URL", "https://the-internet.herokuapp.com"
    ),
    api_base_url=_read_string_environment_variable_or_default(
        "API_BASE_URL", "https://jsonplaceholder.typicode.com"
    ),
    default_action_timeout_ms=_read_int_environment_variable_or_default(
        "DEFAULT_ACTION_TIMEOUT_MS", 10_000
    ),
    default_navigation_timeout_ms=_read_int_environment_variable_or_default(
        "DEFAULT_NAVIGATION_TIMEOUT_MS", 30_000
    ),
    log_level=_read_log_level_environment_variable_or_default("LOG_LEVEL", "info"),
)
