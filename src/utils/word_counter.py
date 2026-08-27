import re
from collections import Counter

_BRACKET_CONTENT_PATTERN = re.compile(r"\[[^\]]*\]")
_WORD_PATTERN = re.compile(r"[a-z0-9]+")


def get_word_occurrence_counts(text: str) -> Counter[str]:
    text_without_brackets = _BRACKET_CONTENT_PATTERN.sub(" ", text)
    return Counter(_WORD_PATTERN.findall(text_without_brackets.lower()))


def print_word_occurrence_counts(label: str, word_occurrence_counts: Counter[str]) -> None:
    print(f"{label} word occurrence counts:")
    for word, occurrence_count in word_occurrence_counts.most_common():
        print(f"{word}: {occurrence_count}")


def get_unique_word_count(word_occurrence_counts: Counter[str]) -> int:
    return len(word_occurrence_counts)
