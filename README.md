# python-automation-framework

## Why this framework

This is a small Python + Playwright framework built for a test automation
assignment. The goal was to keep tests easy to write and easy to read: two
base classes — one for web pages, one for API calls — hold all the shared,
repeated logic (opening pages, clicking, sending requests, logging), so each
page, API client, and test only contains what's actually different about it.

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
  utils/             # strings.json/loader, word-counting helpers

tests/
  ui/                # UI tests
```

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
