import re

_REF_TAG_PATTERN = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.DOTALL)
_TEMPLATE_PATTERN = re.compile(r"\{\{[^{}]*\}\}")
_WIKILINK_PATTERN = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]")
_HEADING_MARKUP_PATTERN = re.compile(r"={2,6}\s*(.*?)\s*={2,6}")


def clean_wikitext(wikitext: str) -> str:
    text_without_refs = _REF_TAG_PATTERN.sub("", wikitext)
    text_without_templates = _TEMPLATE_PATTERN.sub("", text_without_refs)
    text_without_wikilinks = _WIKILINK_PATTERN.sub(r"\1", text_without_templates)
    return _HEADING_MARKUP_PATTERN.sub(r"\1", text_without_wikilinks)
