import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path.cwd() / ".env")

SupportedLogLevel = Literal["debug", "info", "warn", "error"]


def _read_environment_variable_or_none(variable_name: str) -> Optional[str]:
    raw_value = os.environ.get(variable_name)
    if raw_value is None or raw_value.strip() == "":
        return None
    return raw_value.strip()


def _read_string_environment_variable_or_default(variable_name: str, default_value: str) -> str:
    return _read_environment_variable_or_none(variable_name) or default_value


def _read_numeric_environment_variable_or_default(
    variable_name: str, default_value: float
) -> float:
    raw_value = _read_environment_variable_or_none(variable_name)
    if raw_value is None:
        return default_value
    try:
        return float(raw_value)
    except ValueError as error:
        raise ValueError(
            f'Environment variable "{variable_name}" must be a number but got "{raw_value}"'
        ) from error


# TBD: confirm this path convention matches whatever Playwright storage_state
# setup this assignment ends up using (see BrowserContext(storage_state=...)).
AUTH_STATE_PATH = ".auth/user.json"


@dataclass(frozen=True)
class EnvironmentConfiguration:
    ui_base_url: str
    api_base_url: str
    ui_username: str
    ui_password: str
    default_action_timeout_ms: float
    default_navigation_timeout_ms: float
    log_level: SupportedLogLevel


# TBD: the defaults below are a placeholder shape carried over from the demo
# targets in fullFramework — replace base URLs / credentials / timeouts to
# match whatever assignment this framework is pointed at.
environment_configuration = EnvironmentConfiguration(
    ui_base_url=_read_string_environment_variable_or_default(
        "UI_BASE_URL", "https://the-internet.herokuapp.com"
    ),
    api_base_url=_read_string_environment_variable_or_default(
        "API_BASE_URL", "https://jsonplaceholder.typicode.com"
    ),
    ui_username=_read_string_environment_variable_or_default("UI_USERNAME", "tomsmith"),
    ui_password=_read_string_environment_variable_or_default("UI_PASSWORD", "SuperSecretPassword!"),
    default_action_timeout_ms=_read_numeric_environment_variable_or_default(
        "DEFAULT_ACTION_TIMEOUT_MS", 10_000
    ),
    default_navigation_timeout_ms=_read_numeric_environment_variable_or_default(
        "DEFAULT_NAVIGATION_TIMEOUT_MS", 30_000
    ),
    log_level=_read_string_environment_variable_or_default("LOG_LEVEL", "info"),  # type: ignore[arg-type]
)
