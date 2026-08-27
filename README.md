# python-automation-framework

A simple starter framework for testing websites and APIs with Python and Playwright.

This is a base you build on. It gives you the shared building blocks —
you add your own pages, API clients, and tests on top.

## What's inside

- **Playwright** – opens browsers and calls APIs
- **pytest** – runs the tests
- **BasePage** – shared actions for web pages (navigate, click, read rendered text)
- **BaseApiClient** – shared actions for API calls (send request, read response)
- **Logger** – clear, timestamped logs
- **strings.json** – page text (labels, button names, messages) in one place

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in relevant info.

## Run tests

```bash
source .venv/bin/activate   # each new terminal
pytest
```

More ways to run:

```bash
pytest tests/ui              # only UI tests
pytest tests/api             # only API tests
pytest -k "wikipedia"        # tests matching a name
pytest --headed              # show the browser
pytest -v                    # show PASSED/FAILED per test
```

After a run, open the report:

```bash
open playwright-report/report.html
```

## Folders

```
src/
  pages/            # Page objects — one file per web page
  api/               # API clients — one file per API resource
  config/            # Reads settings from .env
  infrastructure/    # Logger
  utils/             # strings.json and its loader

tests/
  ui/                # UI tests
  api/               # API tests
```

## How a test works

A UI test reaches its page object through a fixture — never by
instantiating it directly. A page object extends `BasePage` and only
talks to Playwright through it:

```python
def test_example(wikipedia_test_automation_page: WikipediaTestAutomationPage) -> None:
    wikipedia_test_automation_page.open_wikipedia_test_automation_page()
    wikipedia_test_automation_page.click_test_driven_development_table_of_contents_link()
```

An API test uses an API client. An API client extends `BaseApiClient`:

```python
client = WikipediaApiClient(api_request_context)
section_text = client.get_section_text(page_title)
```

## Rules to follow

1. Use Playwright's built-in locators (`get_by_role`, `get_by_label`, ...).
   Do not use CSS or XPath.
2. Every page action goes through `BasePage`. Every API call goes through
   `BaseApiClient`.
3. Page text (labels, button names, messages) goes in `strings.json`, not
   hard-coded in the page file.
4. Keep methods small — one method, one action. Combine small methods into
   one bigger method when it's reused across tests.
5. A test always reaches a page object through its fixture in `conftest.py`
   — never `SomePage(page)` directly inside a test.

## Known improvements

- `WikipediaApiClient.get_section_text` uses a hard-coded section index
  (`_TEST_DRIVEN_DEVELOPMENT_SECTION_INDEX`) instead of looking it up via
  Wikipedia's `action=parse&prop=sections` endpoint. The lookup call worked, but
  firing it right before the content request tripped Wikipedia's rate limiting
  (HTTP 429) on the second call. A real fix would send a proper `User-Agent`
  header (Wikipedia's API policy expects one identifying the client) and/or add
  retry/backoff, then restore the dynamic lookup.

## Checks before you commit

```bash
ruff check .      # style
mypy              # types
pytest            # tests
```
