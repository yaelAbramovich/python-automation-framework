from abc import ABC

from playwright.sync_api import Locator, Page

from src.infrastructure.logger import Logger


class BasePage(ABC):
    """
    BasePage holds every shared Playwright action used by page objects.
    Every concrete page object must extend this class.

    Locators are defined inside each concrete page object using Playwright's
    semantic locators directly (self.page.get_by_role, get_by_label,
    get_by_text, get_by_placeholder, get_by_test_id, ...). BasePage does NOT
    wrap them — it only consumes Locator instances inside its shared actions.
    """

    def __init__(self, page: Page) -> None:
        if type(self) is BasePage:
            raise TypeError("BasePage is abstract and cannot be instantiated directly")
        self._page = page
        self._logger = Logger(type(self).__name__)

    def _navigate_to_url_path(self, url_path: str) -> None:
        self._logger.info(f"Navigating to URL: {url_path}")
        self._page.goto(url_path)

    def _click_on_element(self, element_locator: Locator, element_description: str) -> None:
        self._logger.info(f"Clicking on element: {element_description}")
        element_locator.click()

    def _get_rendered_text_from_element(
        self, element_locator: Locator, element_description: str
    ) -> str:
        self._logger.info(f"Getting rendered text from element: {element_description}")
        return element_locator.inner_text()
