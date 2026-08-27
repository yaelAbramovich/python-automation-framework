from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_DROPDOWN_PAGE_STRINGS = strings["pages"]["dropdown"]

_OPTION_VALUES_BY_LABEL: dict[str, str] = {
    "Option 1": "1",
    "Option 2": "2",
}


class DropdownPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._dropdown_select = page.get_by_role("combobox").describe("Dropdown select")

    def open(self) -> None:
        self._navigate_to_url_path(_DROPDOWN_PAGE_STRINGS["url_path"])

    def select_dropdown_option(self, option_label: str) -> None:
        self._select_option_from_dropdown(self._dropdown_select, option_label, "Dropdown select")

    def assert_dropdown_option_is_selected(self, expected_label: str) -> None:
        expected_value = _OPTION_VALUES_BY_LABEL[expected_label]
        self._assert_element_has_value(self._dropdown_select, expected_value, "Dropdown select")
