from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_WIKI_PAGE_STRINGS = strings["pages"]["wikipedia_test_automation"]


class WikipediaTestAutomationPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        toc_navigation = page.get_by_role(
            "navigation", name=_WIKI_PAGE_STRINGS["toc_navigation_accessible_name"]
        ).describe("Table of contents navigation")
        self._test_driven_development_toc_link = toc_navigation.get_by_role(
            "link", name=_WIKI_PAGE_STRINGS["test_driven_development_heading_text"]
        ).describe("Test-driven development table of contents link")
        self._main_content = page.get_by_role("main").describe("Article main content")

    def open(self) -> None:
        self._navigate_to_url_path(_WIKI_PAGE_STRINGS["url_path"])

    def click_test_driven_development_toc_link(self) -> None:
        self._click_on_element(
            self._test_driven_development_toc_link,
            "Test-driven development table of contents link",
        )

    def get_test_driven_development_section_text(self) -> str:
        heading = _WIKI_PAGE_STRINGS["test_driven_development_heading_text"]
        next_heading = _WIKI_PAGE_STRINGS["next_section_heading_text"]
        lines = self._get_rendered_text_from_element(
            self._main_content, "Article main content"
        ).splitlines()

        start_index = next(i for i, line in enumerate(lines) if line.startswith(heading))
        end_index = next(
            i for i, line in enumerate(lines) if i > start_index and line.startswith(next_heading)
        )
        body_lines = lines[start_index + 1 : end_index]

        return heading + "\n" + "\n".join(body_lines)
