from playwright.sync_api import APIRequestContext

from src.api.wikipedia_api_client import WikipediaApiClient
from src.pages.wikipedia_test_automation_page import WikipediaTestAutomationPage
from src.utils.strings import strings
from src.utils.word_counter import get_word_occurrence_counts, print_word_occurrence_counts

_WIKI_PAGE_STRINGS = strings["pages"]["wikipedia_test_automation"]


def test_unique_word_count_matches_between_ui_and_api(
    wikipedia_test_automation_page: WikipediaTestAutomationPage,
    api_request_context: APIRequestContext,
) -> None:
    wikipedia_test_automation_page.open_wikipedia_test_automation_page()
    wikipedia_test_automation_page.click_test_driven_development_table_of_contents_link()

    ui_section_raw_text = (
        wikipedia_test_automation_page.get_test_driven_development_section_raw_text()
    )
    ui_word_occurrence_counts = get_word_occurrence_counts(ui_section_raw_text)
    ui_unique_word_count = print_word_occurrence_counts("UI", ui_word_occurrence_counts)
    print("-" * 40)

    wikipedia_api_client = WikipediaApiClient(api_request_context)
    api_section_text = wikipedia_api_client.get_section_text(_WIKI_PAGE_STRINGS["page_title"])
    api_word_occurrence_counts = get_word_occurrence_counts(api_section_text)
    api_unique_word_count = print_word_occurrence_counts("API", api_word_occurrence_counts)

    assert ui_unique_word_count == api_unique_word_count, (
        f"Expected UI unique word count ({ui_unique_word_count}) to match "
        f"API unique word count ({api_unique_word_count})"
    )
