from src.pages.wikipedia_test_automation_page import WikipediaTestAutomationPage
from src.utils.word_counter import count_words


def test_wikipedia_ui_word_count(
    wikipedia_test_automation_page: WikipediaTestAutomationPage,
) -> None:
    wikipedia_test_automation_page.open_wikipedia_test_automation_page()
    wikipedia_test_automation_page.click_test_driven_development_table_of_contents_link()

    section_text = wikipedia_test_automation_page.get_test_driven_development_section_raw_text()
    word_counts = count_words(section_text)

    for word, count in word_counts.most_common():
        print(f"{word}: {count}")

    print(f"unique word count: {len(word_counts)}")
