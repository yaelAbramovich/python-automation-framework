# python-automation-framework

A reusable Python + Playwright test automation base framework. It's the
"main" starting point for spinning up UI/API test suites quickly per job
assignment — a thin, opinionated core, not a finished test suite.

Structurally mirrors [fullFramework](https://github.com/yaelAbramovich/fullFramework)
(the TypeScript/Playwright equivalent), translated to idiomatic Python:
sync Playwright API, pytest, snake_case modules.

## Tech stack

- **Python 3.9+**
- **Playwright (sync API)** — browser automation + API request context
- **pytest** + **pytest-playwright** — test runner and fixtures
- **pytest-html** — HTML test report (all results, not just failures)
- **ruff** — linting
- **mypy** — type checking
- **python-dotenv** — `.env` loading

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in `UI_USERNAME`/`UI_PASSWORD` —
those two are required with no default and the app will fail to start
without them. Everything else (base URLs, timeouts, log level) is optional
and only needs setting to override its default — see
`src/config/environment.py` for the full list of variables and their
defaults.

## Running tests

```bash
source .venv/bin/activate   # each new terminal session

pytest                                    # everything
pytest tests/ui                           # UI tests only
pytest tests/api                          # API tests only
pytest tests/ui/test_example_login.py -v  # one file, verbose
pytest --headed                           # UI tests with a visible browser
pytest -k "login"                         # filter by name
pytest -m smoke                           # filter by marker (see pytest.ini)
```

Every run generates `playwright-report/report.html` (lists all tests, pass
or fail — open with `open playwright-report/report.html`). Screenshots,
video, and trace are captured only on failure (`test-results/`), per
Playwright best practices.

## Project structure

```
src/
  api/
    base_api_client.py     # BaseApiClient — wraps APIRequestContext, adds logging
  config/
    environment.py         # single source of truth for env vars (typed, defaulted)
  infrastructure/
    logger.py               # Logger — leveled, timestamped console logging
    fixtures.py              # empty — placeholder for future shared pytest fixtures
  pages/
    base_page.py            # BasePage — shared navigate/click/fill/assert helpers
  utils/
    strings.json             # empty — placeholder for page-string constants

tests/
  api/                      # API test specs
  ui/                       # UI test specs

conftest.py                 # base_url + per-page timeouts + api_request_context fixture
pytest.ini                   # pytest-playwright CLI defaults (browser, report, markers)
pyproject.toml               # ruff + mypy config
requirements.txt             # pinned dependency list
.env.example                 # copy to .env; fill in UI_USERNAME/UI_PASSWORD (required, no default)
```

There is no single `playwright.config` file — pytest-playwright splits that
role between `pytest.ini` (CLI-level defaults) and `conftest.py` (fixture
overrides for base URL / timeouts / a custom API request-context fixture).

## Architecture

Every test goes through the two base classes — nothing talks to Playwright's
`Page` or `APIRequestContext` directly:

```
UI test                              API test
  └── ConcretePage(BasePage)           └── ConcreteApiClient(BaseApiClient)
        ├── locators via                    ├── _send_http_request()
        │   page.get_by_*().describe()      └── _parse_response_as_json()
        ├── actions/asserts via
        │   BasePage helpers
        └── logs via Logger
```

`environment.py` is the only place `os.environ` is read — both `BasePage`
and `BaseApiClient` consume `environment_configuration`, never `os.environ`
directly.

See `tests/ui/test_example_login.py` and `tests/api/test_example_posts.py`
for worked examples — each defines a small concrete class local to the test
file (not under `src/`) purely to demonstrate the base classes end-to-end.

## Conventions

- **Locators:** Playwright semantic APIs only (`get_by_role`, `get_by_label`,
  `get_by_text`, `get_by_placeholder`, `get_by_test_id`) — no CSS/XPath.
  Every locator ends with `.describe("...")`.
- **Actions/assertions:** always through `BasePage` helpers
  (`_click_on_element`, `_fill_element_with_text`, `_assert_element_is_visible`,
  etc.) — never call Playwright's `Locator`/`Page` methods directly from a
  page object or test.
- **Web-first assertions only:** `expect(locator).to_be_visible()` style
  (auto-retrying). Never `assert locator.is_visible()` and never
  `locator.wait_for()` as a pre-action gate.
- **API paths** live on the concrete client as constants, not in
  `strings.json` — that file is reserved for UI page strings.

## CI

`.github/workflows/playwright.yml` — manual (`workflow_dispatch`) for now.
Runs `ruff check` → `mypy` → API tests → UI tests (chromium only), uploads
the HTML report as an artifact. A `tag` input (`all`/`smoke`/`regression`/
`login`) filters by pytest marker once tests are decorated with one.

## Intentionally not included yet

- **`PageManager`** — the TS version's page-object-manager pattern. Not
  ported; revisit once there's a real multi-page suite to manage.
- **`create-pom` skill** — fullFramework has a Claude Code skill that
  generates POMs; the Python version assumes `PageManager`, so it's on hold
  until that decision is made.
- Cross-browser projects (firefox/webkit), CI-only retries, and parallel
  workers — straightforward to add (`pytest-rerunfailures`, `pytest-xdist`)
  but not wired up yet.
