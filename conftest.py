from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from src.config.environment import environment_configuration
from src.pages.wikipedia_test_automation_page import WikipediaTestAutomationPage

# Root pytest-playwright fixtures — CLI-level defaults live in pytest.ini.


@pytest.fixture
def page(page: Page) -> Page:
    page.set_default_timeout(environment_configuration.default_action_timeout_ms)
    page.set_default_navigation_timeout(environment_configuration.default_navigation_timeout_ms)
    return page


@pytest.fixture
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """
    pytest-playwright has no built-in API request fixture (unlike @playwright/test's
    `request`), so it's created here directly.
    """
    request_context = playwright.request.new_context()
    yield request_context
    request_context.dispose()


@pytest.fixture
def wikipedia_test_automation_page(page: Page) -> WikipediaTestAutomationPage:
    return WikipediaTestAutomationPage(page)
