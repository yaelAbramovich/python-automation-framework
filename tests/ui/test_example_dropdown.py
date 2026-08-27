from src.pages.dropdown_page import DropdownPage
from src.utils.strings import strings

_DROPDOWN_PAGE_STRINGS = strings["pages"]["dropdown"]


def test_selecting_option_one_updates_dropdown_value(dropdown_page: DropdownPage) -> None:
    dropdown_page.open()

    dropdown_page.select_dropdown_option(_DROPDOWN_PAGE_STRINGS["option_one_label"])

    dropdown_page.assert_dropdown_option_is_selected(_DROPDOWN_PAGE_STRINGS["option_one_label"])
