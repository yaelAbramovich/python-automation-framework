# CLAUDE.md

This file gives Claude Code the context it needs to work in this repo.

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate  # first time only
pip install -r requirements.txt                     # install dependencies
playwright install chromium                         # install browser
ruff check .                                        # lint
mypy                                                 # typecheck (src/ only)
pytest                                               # run all tests
pytest tests/ui                                      # only UI specs
pytest tests/api                                     # only API specs
pytest --headed                                      # UI tests, visible browser
open playwright-report/report.html                   # last HTML report
```

Run one test, by name, or by line:
```bash
pytest tests/ui/test_example_login.py       # one file
pytest -k "login"                           # by name
pytest tests/ui/test_example_login.py:8     # file + line
pytest -m smoke                             # by marker (see pytest.ini)
```

There's no single `playwright.config` file. Python splits that job in two:
- `pytest.ini` — CLI defaults (browser, screenshot/video/trace, markers)
- `conftest.py` — fixture overrides (base URL, timeouts, the custom `api_request_context` fixture)

## Architecture

Two base classes hold everything. No test or page object talks to Playwright's `Page` or
`APIRequestContext` directly.

- `environment.py` — the one source of config
- `strings.json` — the one source of page text
- `logger.py` — gives every base class its logging for free

**UI test flow:**
```
test_*.py
  └── ConcretePage(BasePage)          -> src/pages/<name>_page.py
        ├── locators via              this.page.get_by_*(...).describe(...)
        ├── actions/asserts via        BasePage helpers
        ├── page text via              src/utils/strings.json
        └── logs via                   src/infrastructure/logger.py
```

**API test flow:**
```
test_*.py
  └── ConcreteClient(BaseApiClient)   -> src/api/<name>_api_client.py
        ├── _send_http_request(...)
        └── _parse_response_as_json(...)
```

**Config.** `environment.py` is the only place `os.environ` is read. It builds a typed, validated
`environment_configuration` object that everything else imports. Add a new env var there first —
never read `os.environ` anywhere else. `UI_USERNAME` and `UI_PASSWORD` are required and fail fast
if missing. Everything else has a default. `.env.example` lists them all.

**Logging.** Every `Logger(...)` is built as `Logger(type(self).__name__)` inside `BasePage` and
`BaseApiClient`. A concrete class never passes its own logger name.

**Key files outside `src/`:**

| File | What it's for |
|---|---|
| `conftest.py` | Fixture overrides — sets `base_url` and timeouts from config, adds `api_request_context` (pytest-playwright has no built-in one). |
| `pytest.ini` | CLI defaults: browser, screenshot/video/trace capture, HTML report path, markers. |
| `pyproject.toml` | `ruff` and `mypy` config. |
| `requirements.txt` | Pinned dependencies. |
| `.env.example` | Every configurable env var. `UI_USERNAME`/`UI_PASSWORD` are required; the rest show their real defaults. |

## Conventions to follow

1. **Page text lives in `strings.json`.** Labels, URL paths, and user-facing messages go under
   `pages.<page>.*`, snake_case keys, loaded once via `strings.py`. Only product text goes here —
   text a real user would actually see on the page. API paths and log/description text stay out of
   it — those live on the client/page code itself, since they serve a different purpose (internal
   logging, not user-facing text).

2. **POMs extend `BasePage`; API clients extend `BaseApiClient`.** These are the only classes that
   touch Playwright's `Locator`/`Page`/`APIRequestContext` directly.

3. **Locators: Playwright's semantic APIs only.** `get_by_role`, `get_by_label`, `get_by_text`,
   `get_by_placeholder`, `get_by_test_id`. Never `page.locator(css_or_xpath)`.

4. **Every locator ends with `.describe(...)`** for readable trace/report output.

5. **Web-first assertions only.** Use `self._assert_element_is_visible(...)`, never
   `assert locator.is_visible()` or `locator.wait_for()` as a pre-action gate.

6. **Every assert needs a message.** A plain `assert x == y` with no message is hard to debug on
   failure — say what was expected and what was actually found (see `tests/api/test_example_posts.py`
   for the pattern). `BasePage`'s web-first assertions already get this for free via the
   `element_description` argument.

7. **`BasePage` only gets generic assertions.** Its assert methods (`_assert_element_is_visible`,
   `_assert_element_contains_text`, etc.) work on any locator and know nothing about a specific
   page. An assertion that's specific to one page (e.g. "login succeeded") belongs on that page's
   own class — see `LoginPage.assert_flash_message_contains` — never on `BasePage`.

8. **Small methods, then one that combines them.** `fill_username_input`, `click_login_button`,
   etc. each do one thing. A method like `login` calls them in sequence. Keep both — a negative
   test might only need the small ones.

9. **Mask any sensitive value on purpose, not by guessing.** This isn't only about
   `_fill_element_with_text(...)`'s `sensitive=True` param — any time code logs a value that could
   be a password, token, secret, or other sensitive data (now or in a method added later), mask it
   explicitly at that call site. There's no auto-detection by keyword; every call site decides for
   itself.

10. **Logger names are automatic.** Don't add a `logger_name` parameter back to `BasePage` or
    `BaseApiClient` — it's derived from the class name already.

11. **mypy only checks `src/`, not `tests/`.** Code moved from a test file into `src/` may need
    type annotations it didn't need before.

## Adding things

- **New page:** add its text to `strings.json` under `pages.<name>.*`. Create
  `src/pages/<name>_page.py` extending `BasePage`, build locators from `strings.py`, add small
  methods plus a combined one where it helps. Also add whatever assertion methods make sense for
  that page (e.g. "form shows this error") — on the page class itself, never on `BasePage`.
- **New API client:** create `src/api/<name>_api_client.py` extending `BaseApiClient`. Keep paths
  as class constants — not in `strings.json`. Also add whatever assertion/validation methods make
  sense for that resource (e.g. "response matches the expected shape") — on the client itself,
  never on `BaseApiClient`.
- **New env var:** add it to `.env.example`, then to `EnvironmentConfiguration` and
  `environment_configuration` in `environment.py`. Validate it if the value has rules (see
  `_read_log_level_environment_variable_or_default` for the pattern).

## CI

`.github/workflows/playwright.yml` runs manually for now (`workflow_dispatch`), with a `tag` input
(`all`/`smoke`/`regression`/`login`) to filter by pytest marker. It runs `ruff check` → `mypy` →
API tests → UI tests (chromium only), then uploads the HTML report.
