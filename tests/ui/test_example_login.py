from playwright.sync_api import Page

from src.config.environment import environment_configuration
from src.pages.base_page import BasePage


class _ExampleLoginPage(BasePage):
    """
    Minimal concrete page object demonstrating BasePage against
    the-internet.herokuapp.com/login. Local to this example test, not part
    of the reusable src/pages framework.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, "ExampleLoginPage")
        self._username_field = page.get_by_label("Username").describe("Username input field")
        self._password_field = page.get_by_label("Password").describe("Password input field")
        self._submit_button = page.get_by_role("button", name="Login").describe(
            "Login submit button"
        )

    def open(self) -> None:
        self._navigate_to_url_path("/login")

    def login_with(self, username: str, password: str) -> None:
        self._fill_element_with_text(self._username_field, username, "Username input field")
        self._fill_element_with_text(self._password_field, password, "Password input field")
        self._click_on_element(self._submit_button, "Login submit button")

    def assert_flash_message_contains(self, expected_fragment: str) -> None:
        flash_locator = self._page.get_by_text(expected_fragment).describe(
            f'Flash message containing "{expected_fragment}"'
        )
        self._assert_element_is_visible(
            flash_locator, f'Flash message containing "{expected_fragment}"'
        )


def test_login_with_valid_credentials_shows_success_message(page: Page) -> None:
    login_page = _ExampleLoginPage(page)

    login_page.open()
    login_page.login_with(
        environment_configuration.ui_username, environment_configuration.ui_password
    )

    login_page.assert_flash_message_contains("You logged into a secure area!")
