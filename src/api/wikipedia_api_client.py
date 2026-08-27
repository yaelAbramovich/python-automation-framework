import re

from src.api.base_api_client import BaseApiClient, HttpMethod, HttpRequestOptions

_REF_TAG_PATTERN = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.DOTALL)
_TEMPLATE_PATTERN = re.compile(r"\{\{[^{}]*\}\}")
_WIKILINK_PATTERN = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]")
_HEADING_MARKUP_PATTERN = re.compile(r"={2,6}\s*(.*?)\s*={2,6}")


def _clean_wikitext(wikitext: str) -> str:
    text_without_refs = _REF_TAG_PATTERN.sub("", wikitext)
    text_without_templates = _TEMPLATE_PATTERN.sub("", text_without_refs)
    text_without_wikilinks = _WIKILINK_PATTERN.sub(r"\1", text_without_templates)
    return _HEADING_MARKUP_PATTERN.sub(r"\1", text_without_wikilinks)


class WikipediaApiClient(BaseApiClient):
    _API_URL = "https://en.wikipedia.org/w/api.php"

    # Hard-coded instead of looked up via the `action=parse&prop=sections` endpoint — see
    # "Known improvements" in README.md for why.
    _TEST_DRIVEN_DEVELOPMENT_SECTION_INDEX = "8"

    def _get_section_wikitext(self, page_title: str, section_index: str) -> str:
        response = self._send_http_request(
            HttpMethod.GET,
            self._API_URL,
            HttpRequestOptions(
                query_parameters={
                    "action": "query",
                    "titles": page_title,
                    "prop": "revisions",
                    "rvprop": "content",
                    "rvslots": "main",
                    "rvsection": section_index,
                    "format": "json",
                }
            ),
        )
        self._assert_response_is_ok(response)

        pages = self._parse_response_as_json(response)["query"]["pages"]
        page = next(iter(pages.values()))
        return page["revisions"][0]["slots"]["main"]["*"]

    def get_section_text(self, page_title: str) -> str:
        wikitext = self._get_section_wikitext(
            page_title, self._TEST_DRIVEN_DEVELOPMENT_SECTION_INDEX
        )
        return _clean_wikitext(wikitext)
