from abc import ABC

from playwright.sync_api import Locator, Page, expect

from src.infrastructure.logger import Logger


class BasePage(ABC):
    """
    BasePage holds every shared Playwright action used by page objects.
    Every concrete page object must extend this class.

    Locators are defined inside each concrete page object using Playwright's
    semantic locators directly (self.page.get_by_role, get_by_label,
    get_by_text, get_by_placeholder, get_by_test_id, ...). BasePage does NOT
    wrap them — it only consumes Locator instances inside its shared actions.

    Waiting strategy follows Playwright best practices
    (https://playwright.dev/python/docs/best-practices):
      - Actions (click, fill, ...) auto-wait for actionability — no manual
        wait is needed before calling them.
      - For visibility / text / state checks use web-first assertions
        (expect(locator).to_be_visible() etc.), which auto-retry until the
        timeout is reached.
      - Do NOT use locator.wait_for() as a pre-action gate, and do NOT assert
        on locator.is_visible() directly — those don't retry.
    """

    def __init__(self, page: Page, page_logger_name: str) -> None:
        if type(self) is BasePage:
            raise TypeError("BasePage is abstract and cannot be instantiated directly")
        self._page = page
        self._logger = Logger(page_logger_name)

    # ---------- Navigation ----------

    def _navigate_to_url_path(self, url_path: str) -> None:
        self._logger.info(f"Navigating to URL: {url_path}")
        self._page.goto(url_path)

    def get_current_page_url(self) -> str:
        return self._page.url

    def get_current_page_title(self) -> str:
        return self._page.title()

    # ---------- Actions (Playwright auto-waits for actionability) ----------

    def _click_on_element(self, element_locator: Locator, element_description: str) -> None:
        self._logger.info(f"Clicking on element: {element_description}")
        element_locator.click()

    def _fill_element_with_text(
        self, element_locator: Locator, text_value: str, element_description: str
    ) -> None:
        self._logger.info(f'Filling element "{element_description}" with text: {text_value}')
        element_locator.fill(text_value)

    def _get_visible_text_from_element(
        self, element_locator: Locator, element_description: str
    ) -> str:
        self._logger.info(f"Getting text from element: {element_description}")
        text_content = element_locator.text_content()
        return (text_content or "").strip()

    # ---------- Web-first assertions (auto-retry until timeout) ----------

    def _assert_element_is_visible(
        self, element_locator: Locator, element_description: str
    ) -> None:
        self._logger.debug(f"Asserting element is visible: {element_description}")
        expect(element_locator, element_description).to_be_visible()

    def _assert_element_is_hidden(
        self, element_locator: Locator, element_description: str
    ) -> None:
        self._logger.debug(f"Asserting element is hidden: {element_description}")
        expect(element_locator, element_description).to_be_hidden()

    def _assert_element_has_exact_text(
        self, element_locator: Locator, expected_text: str, element_description: str
    ) -> None:
        self._logger.debug(
            f'Asserting element "{element_description}" has exact text: {expected_text}'
        )
        expect(element_locator, element_description).to_have_text(expected_text)

    def _assert_element_contains_text(
        self, element_locator: Locator, expected_text: str, element_description: str
    ) -> None:
        self._logger.debug(
            f'Asserting element "{element_description}" contains text: {expected_text}'
        )
        expect(element_locator, element_description).to_contain_text(expected_text)
