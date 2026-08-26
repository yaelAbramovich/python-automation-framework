from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_LOGIN_STRINGS = strings["pages"]["login"]


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._username_field = page.get_by_label(_LOGIN_STRINGS["usernameFieldLabel"]).describe(
            "Username input field"
        )
        self._password_field = page.get_by_label(_LOGIN_STRINGS["passwordFieldLabel"]).describe(
            "Password input field"
        )
        self._submit_button = page.get_by_role(
            "button", name=_LOGIN_STRINGS["submitButtonAccessibleName"]
        ).describe("Login submit button")

    def open(self) -> None:
        self._navigate_to_url_path(_LOGIN_STRINGS["urlPath"])

    def fill_username_field(self, username: str) -> None:
        self._fill_element_with_text(self._username_field, username, "Username input field")

    def fill_password_field(self, password: str) -> None:
        self._fill_element_with_text(
            self._password_field, password, "Password input field", sensitive=True
        )

    def click_login_submit_button(self) -> None:
        self._click_on_element(self._submit_button, "Login submit button")

    def login_with(self, username: str, password: str) -> None:
        self.fill_username_field(username)
        self.fill_password_field(password)
        self.click_login_submit_button()

    def assert_flash_message_contains(self, expected_fragment: str) -> None:
        flash_locator = self._page.get_by_text(expected_fragment).describe(
            f'Flash message containing "{expected_fragment}"'
        )
        self._assert_element_is_visible(
            flash_locator, f'Flash message containing "{expected_fragment}"'
        )
