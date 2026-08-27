import re
from collections import Counter

_BRACKET_CONTENT_PATTERN = re.compile(r"\[[^\]]*\]")
_WORD_PATTERN = re.compile(r"[a-z0-9]+")


def get_word_occurrence_counts(text: str) -> Counter[str]:
    text_without_brackets = _BRACKET_CONTENT_PATTERN.sub(" ", text)
    return Counter(_WORD_PATTERN.findall(text_without_brackets.lower()))


def print_word_occurrence_counts(label: str, word_occurrence_counts: Counter[str]) -> int:
    print(f"{label} word occurrence counts:")
    for word, occurrence_count in word_occurrence_counts.most_common():
        print(f"{word}: {occurrence_count}")

    unique_word_count = len(word_occurrence_counts)
    print(f"{label} unique word count: {unique_word_count}")
    return unique_word_count
