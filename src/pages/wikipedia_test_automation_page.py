from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_WIKI_PAGE_STRINGS = strings["pages"]["wikipedia_test_automation"]

# Wikipedia renders every section heading (any level) with a trailing "edit" link, which
# `inner_text()` flattens onto the heading line with no separator (e.g. "Otheredit"). That
# makes it a reliable, section-name-agnostic marker for "this line is a heading".
_SECTION_HEADING_EDIT_LINK_SUFFIX = "edit"


class WikipediaTestAutomationPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        table_of_contents_navigation = page.get_by_role(
            "navigation", name=_WIKI_PAGE_STRINGS["table_of_contents_navigation_accessible_name"]
        ).describe("Table of contents navigation")
        self._test_driven_development_table_of_contents_link = (
            table_of_contents_navigation.get_by_role(
                "link", name=_WIKI_PAGE_STRINGS["test_driven_development_heading_text"]
            ).describe("Test-driven development table of contents link")
        )
        self._main_content = page.get_by_role("main").describe("Article main content")

    def open_wikipedia_test_automation_page(self) -> None:
        self._navigate_to_url_path(_WIKI_PAGE_STRINGS["url_path"])

    def click_test_driven_development_table_of_contents_link(self) -> None:
        self._click_on_element(
            self._test_driven_development_table_of_contents_link,
            "Test-driven development table of contents link",
        )

    def get_test_driven_development_section_raw_text(self) -> str:
        return self._get_section_raw_text(
            _WIKI_PAGE_STRINGS["test_driven_development_heading_text"]
        )

    def _get_section_raw_text(self, section_heading: str) -> str:
        lines = self._get_rendered_text_from_element(
            self._main_content, "Article main content"
        ).splitlines()

        section_start_index = (
            next(index for index, line in enumerate(lines) if line.startswith(section_heading))
            + 1
        )
        section_end_index = next(
            (
                index
                for index, line in enumerate(lines[section_start_index:], start=section_start_index)
                if line.endswith(_SECTION_HEADING_EDIT_LINK_SUFFIX)
            ),
            len(lines),
        )

        section_body_lines = lines[section_start_index:section_end_index]
        return section_heading + "\n" + "\n".join(section_body_lines)
