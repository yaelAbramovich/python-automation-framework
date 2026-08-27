import re
from collections import Counter

_BRACKET_CONTENT_PATTERN = re.compile(r"\[[^\]]*\]")
_WORD_PATTERN = re.compile(r"[a-z0-9]+")


def get_word_occurrence_counts(text: str) -> Counter[str]:
    text_without_brackets = _BRACKET_CONTENT_PATTERN.sub(" ", text)
    return Counter(_WORD_PATTERN.findall(text_without_brackets.lower()))
