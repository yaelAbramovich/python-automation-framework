from playwright.sync_api import Page

from src.config.environment import environment_configuration
from src.pages.login_page import LoginPage
from src.utils.strings import strings


def test_login_with_valid_credentials_shows_success_message(page: Page) -> None:
    login_page = LoginPage(page)

    login_page.open()
    login_page.login(
        environment_configuration.ui_username, environment_configuration.ui_password
    )

    login_page.assert_flash_message_contains(strings["pages"]["login"]["login_success_message"])
