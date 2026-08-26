from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from src.config.environment import environment_configuration

# Root pytest-playwright fixtures — CLI-level defaults live in pytest.ini.


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "base_url": environment_configuration.ui_base_url,
    }


@pytest.fixture
def page(page: Page) -> Page:
    page.set_default_timeout(environment_configuration.default_action_timeout_ms)
    page.set_default_navigation_timeout(environment_configuration.default_navigation_timeout_ms)
    return page


@pytest.fixture
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """
    pytest-playwright has no built-in API request fixture (unlike @playwright/test's
    `request`), so it's created here directly against `api_base_url`.
    """
    request_context = playwright.request.new_context(
        base_url=environment_configuration.api_base_url
    )
    yield request_context
    request_context.dispose()
