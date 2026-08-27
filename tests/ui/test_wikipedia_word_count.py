from src.pages.wikipedia_test_automation_page import WikipediaTestAutomationPage
from src.utils.word_counter import get_word_occurrence_counts


def test_wikipedia_ui_word_count(
    wikipedia_test_automation_page: WikipediaTestAutomationPage,
) -> None:
    wikipedia_test_automation_page.open_wikipedia_test_automation_page()
    wikipedia_test_automation_page.click_test_driven_development_table_of_contents_link()

    section_raw_text = (
        wikipedia_test_automation_page.get_test_driven_development_section_raw_text()
    )
    word_occurrence_counts = get_word_occurrence_counts(section_raw_text)

    for word, occurrence_count in word_occurrence_counts.most_common():
        print(f"{word}: {occurrence_count}")

    actual_unique_word_count = len(word_occurrence_counts)
    print(f"unique word count: {actual_unique_word_count}")
