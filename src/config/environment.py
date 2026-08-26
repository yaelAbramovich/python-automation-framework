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


def _read_required_string_environment_variable(variable_name: str) -> str:
    raw_value = _read_environment_variable_or_none(variable_name)
    if raw_value is None:
        raise ValueError(
            f'Environment variable "{variable_name}" is required but not set. '
            "Set it in your .env file (see .env.example)."
        )
    return raw_value


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


# Not yet wired up to a real auth flow — this is where Playwright's
# BrowserContext(storage_state=...) would read/write saved session state
# once a login-based setup exists. Playwright accepts a Path here directly.
AUTH_STATE_PATH = Path(".auth/user.json")


@dataclass(frozen=True)
class EnvironmentConfiguration:
    ui_base_url: str
    api_base_url: str
    ui_username: str
    ui_password: str
    default_action_timeout_ms: int
    default_navigation_timeout_ms: int
    log_level: SupportedLogLevel


# UI_USERNAME/UI_PASSWORD have no defaults on purpose — copy .env.example to
# .env and fill in real credentials before running UI tests.
environment_configuration = EnvironmentConfiguration(
    ui_base_url=_read_string_environment_variable_or_default(
        "UI_BASE_URL", "https://the-internet.herokuapp.com"
    ),
    api_base_url=_read_string_environment_variable_or_default(
        "API_BASE_URL", "https://jsonplaceholder.typicode.com"
    ),
    ui_username=_read_required_string_environment_variable("UI_USERNAME"),
    ui_password=_read_required_string_environment_variable("UI_PASSWORD"),
    default_action_timeout_ms=_read_int_environment_variable_or_default(
        "DEFAULT_ACTION_TIMEOUT_MS", 10_000
    ),
    default_navigation_timeout_ms=_read_int_environment_variable_or_default(
        "DEFAULT_NAVIGATION_TIMEOUT_MS", 30_000
    ),
    log_level=_read_log_level_environment_variable_or_default("LOG_LEVEL", "info"),
)
