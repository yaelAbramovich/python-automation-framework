# python-automation-framework

A simple starter framework for testing websites and APIs with Python and Playwright.

This is a base you build on. It gives you the shared building blocks —
you add your own pages, API clients, and tests on top.

## What's inside

- **Playwright** – opens browsers and calls APIs
- **pytest** – runs the tests
- **BasePage** – shared actions for web pages (click, fill, check text)
- **BaseApiClient** – shared actions for API calls (send request, read response)
- **Logger** – clear, timestamped logs, with password/secret masking
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
pytest -k "login"            # tests matching a name
pytest --headed              # show the browser
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

A UI test uses a page object. A page object extends `BasePage` and only
talks to Playwright through it:

```python
login_page = LoginPage(page)
login_page.open()
login_page.login("tomsmith", "SuperSecretPassword!")
```

An API test uses an API client. An API client extends `BaseApiClient`:

```python
client = PostsApiClient(api_request_context)
response, post = client.get_post_by_id(1)
```

## Rules to follow

1. Use Playwright's built-in locators (`get_by_role`, `get_by_label`, ...).
   Do not use CSS or XPath.
2. Every page action goes through `BasePage`. Every API call goes through
   `BaseApiClient`.
3. Page text (labels, button names, messages) goes in `strings.json`, not
   hard-coded in the page file.
4. Pass `sensitive=True` when filling a password or secret, so it doesn't
   show up in logs.
5. Keep methods small — one method, one action. Combine small methods into
   one bigger method when useful (see `LoginPage.login`).

## Checks before you commit

```bash
ruff check .      # style
mypy              # types
pytest            # tests
```
