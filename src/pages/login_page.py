from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_LOGIN_PAGE_STRINGS = strings["pages"]["login"]


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._username_input = page.get_by_label(
            _LOGIN_PAGE_STRINGS["username_input_label"]
        ).describe("Username input field")
        self._password_input = page.get_by_label(
            _LOGIN_PAGE_STRINGS["password_input_label"]
        ).describe("Password input field")
        self._login_button = page.get_by_role(
            "button", name=_LOGIN_PAGE_STRINGS["login_button_accessible_name"]
        ).describe("Login submit button")

    def open(self) -> None:
        self._navigate_to_url_path(_LOGIN_PAGE_STRINGS["url_path"])

    def fill_username_input(self, username: str) -> None:
        self._fill_element_with_text(self._username_input, username, "Username input field")

    def fill_password_input(self, password: str) -> None:
        self._fill_element_with_text(
            self._password_input, password, "Password input field", sensitive=True
        )

    def click_login_button(self) -> None:
        self._click_on_element(self._login_button, "Login submit button")

    def login(self, username: str, password: str) -> None:
        self.fill_username_input(username)
        self.fill_password_input(password)
        self.click_login_button()

    def assert_flash_message_contains(self, expected_fragment: str) -> None:
        flash_locator = self._page.get_by_text(expected_fragment).describe(
            f'Flash message containing "{expected_fragment}"'
        )
        self._assert_element_is_visible(
            flash_locator, f'Flash message containing "{expected_fragment}"'
        )
