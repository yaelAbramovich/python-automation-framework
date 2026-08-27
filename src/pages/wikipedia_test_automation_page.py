from itertools import dropwhile, takewhile

from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_WIKI_PAGE_STRINGS = strings["pages"]["wikipedia_test_automation"]


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
        heading = _WIKI_PAGE_STRINGS["test_driven_development_heading_text"]
        next_heading = _WIKI_PAGE_STRINGS["next_section_heading_text"]
        lines = self._get_rendered_text_from_element(
            self._main_content, "Article main content"
        ).splitlines()

        lines_after_heading = dropwhile(lambda line: not line.startswith(heading), lines)
        next(lines_after_heading)
        body_lines = takewhile(lambda line: not line.startswith(next_heading), lines_after_heading)

        return heading + "\n" + "\n".join(body_lines)
