# create-pom Python Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the TypeScript `create-pom` Claude Code skill to a `.claude/skills/create-pom/SKILL.md` skill for `python-automation-framework`, matching this repo's real conventions (sync Playwright, pytest fixtures, `ruff`/`mypy`), and prove it works by running it end-to-end against a real page.

**Architecture:** One new skill file drives Playwright MCP to inspect a page and writes a POM under `src/pages/`, a `conftest.py` fixture, and (only genuinely user-facing) text in `strings.json`. Task 1 first migrates the existing `LoginPage` to the fixture pattern the skill will enforce, so the repo has one consistent pattern before the skill exists. Task 3 dogfoods the finished skill against `the-internet.herokuapp.com/dropdown` and keeps the result as a second real example page + test.

**Tech Stack:** Python 3.9, `playwright.sync_api`, pytest / pytest-playwright, `ruff`, `mypy`, Claude Code skills, Playwright MCP.

**Spec:** `docs/superpowers/specs/2026-08-27-create-pom-python-port-design.md`

## Global Constraints

- Target Python 3.9 (`pyproject.toml`: `target-version = "py39"`, mypy `python_version = "3.9"`).
- Line length 100 (`ruff`: `line-length = 100`); `ruff` lint set is `["E", "F", "I", "UP"]`.
- `mypy` checks `src/` only, with `disallow_untyped_defs = true` — every function/method under `src/` needs full type annotations. `conftest.py` and `tests/` are outside mypy's scope but keep annotations anyway to match the existing style.
- Never use `page.locator(css_or_xpath)` — no last-resort fallback exists in this repo (README rule). If no semantic/test-id locator works, stop and ask instead of writing one.
- `.describe()` / `element_description` strings are always inline string literals in the page file — never centralized into `strings.json`. Only genuine user-facing text (`url_path`, labels, accessible names, messages) goes in `strings.json`, under `pages.<snake_case_key>`.
- Every POM is reachable only via a `conftest.py` fixture named after its file (`checkout_page.py` → fixture `checkout_page`). No test may instantiate a page object directly.
- No soft-assertion library or concept — aggregate checks are always multiple small `assert_*` methods.
- No new third-party dependencies.

---

### Task 1: Migrate `LoginPage` to a `conftest.py` fixture

**Files:**
- Modify: `conftest.py`
- Modify: `tests/ui/test_example_login.py`

**Interfaces:**
- Consumes: `LoginPage.__init__(self, page: Page) -> None` (already exists in `src/pages/login_page.py`, unchanged by this task).
- Produces: a `login_page` pytest fixture with signature `def login_page(page: Page) -> LoginPage`, usable by any test that declares a `login_page: LoginPage` parameter.

- [ ] **Step 1: Run the existing test to confirm the baseline passes**

Run: `pytest tests/ui/test_example_login.py -v`
Expected: `1 passed` — this is the behavior the refactor below must not change.

- [ ] **Step 2: Add the `login_page` fixture to `conftest.py`**

Add the import and fixture (keep every existing fixture in the file unchanged):

```python
from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from src.config.environment import environment_configuration
from src.pages.login_page import LoginPage

# Root pytest-playwright fixtures — CLI-level defaults live in pytest.ini.


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "base_url": environment_configuration.ui_base_url,
    }


@pytest.fixture
def page(page: Page) -> Page:
    page.set_default_timeout(environment_configuration.default_action_timeout_ms)
    page.set_default_navigation_timeout(environment_configuration.default_navigation_timeout_ms)
    return page


@pytest.fixture
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """
    pytest-playwright has no built-in API request fixture (unlike @playwright/test's
    `request`), so it's created here directly against `api_base_url`.
    """
    request_context = playwright.request.new_context(
        base_url=environment_configuration.api_base_url
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)
```

- [ ] **Step 3: Update `tests/ui/test_example_login.py` to consume the fixture**

Replace the file's full contents with:

```python
from src.config.environment import environment_configuration
from src.pages.login_page import LoginPage
from src.utils.strings import strings


def test_login_with_valid_credentials_shows_success_message(login_page: LoginPage) -> None:
    login_page.open()
    login_page.login(
        environment_configuration.ui_username, environment_configuration.ui_password
    )

    login_page.assert_flash_message_contains(strings["pages"]["login"]["login_success_message"])
```

(The `Page` import is dropped — the test no longer takes `page` directly, only `login_page`.)

- [ ] **Step 4: Lint and typecheck**

Run: `ruff check . && mypy`
Expected: both exit `0` with no errors.

- [ ] **Step 5: Run the test again to confirm no regression**

Run: `pytest tests/ui/test_example_login.py -v`
Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add conftest.py tests/ui/test_example_login.py
git commit -m "Migrate LoginPage to a conftest.py fixture

Establishes the fixture-per-page pattern the upcoming create-pom skill
will enforce, so new and existing pages follow one convention."
```

---

### Task 2: Author the `create-pom` skill

**Files:**
- Create: `.claude/skills/create-pom/SKILL.md`

**Interfaces:**
- Consumes: `BasePage`'s existing helpers (`_click_on_element`, `_fill_element_with_text`, `_get_visible_text_from_element`, `_assert_element_is_visible`, `_assert_element_is_hidden`, `_assert_element_has_exact_text`, `_assert_element_contains_text`, `_navigate_to_url_path`), the `strings` loader (`from src.utils.strings import strings`), `environment_configuration.ui_base_url`/`ui_username`/`ui_password`, and the `login_page` fixture pattern from Task 1.
- Produces: the `/create-pom` skill, invocable in this repo. It does not export Python symbols itself — it is the thing Task 3 exercises.

- [ ] **Step 1: Create `.claude/skills/create-pom/SKILL.md` with this exact content**

````markdown
---
name: create-pom
description: Generate a pytest/Playwright Page Object for this repo. Drives Playwright MCP to inspect the target page in a live browser, writes the POM under src/pages/, adds user-facing text to src/utils/strings.json, extends BasePage if a helper is missing, and registers the POM as a fixture in conftest.py. Invoked explicitly by the user — never auto-trigger.
argument-hint: [PageClassName]
disable-model-invocation: true
allowed-tools: Bash(ruff check .), Bash(mypy), Bash(pytest --collect-only)
---

# create-pom

Generates a new Page Object for this Playwright/pytest framework. Follows every convention in
this repo's `CLAUDE.md` **and** Playwright's Python best practices at
<https://playwright.dev/python/docs/best-practices> — no exceptions, no shortcuts. If any rule
can't be satisfied, **stop and ask the user**; never silently produce a non-compliant POM.

## Locator priority

Walk this list in order for every interactive element and stop at the first that works:

1. `page.get_by_role("role", name="Accessible Name")`
2. `page.get_by_label("label text")`
3. `page.get_by_placeholder("placeholder text")`
4. `page.get_by_text("visible text")`
5. `page.get_by_title("title text")`
6. `page.get_by_test_id("value")`
7. Chain and filter one of the above — `.filter(has_text="...")`, `.filter(has=child_locator)`,
   or locator chaining into a scoped region — for repeating structures (lists, tables, cards) or
   to scope into a region. Prefer this over any deeper selector.
8. **Never `page.locator(css_or_xpath)`.** This repo's README forbids CSS/XPath outright — there
   is no last-resort fallback. If nothing above works, stop and ask the user whether a
   `data-testid` (or an accessible role/label) can be added to the element.

When unsure between two options, run `playwright codegen <url>` (the pip-installed CLI — it
emits sync Python by default) and use what it picks.

Every locator ends with `.describe("Human-readable element name")` — a **literal string**, never
pulled from `strings.json` (see Strings, below).

## Preflight (every invocation)

- Confirm Playwright MCP tools are reachable. If they aren't, stop and tell the user to start the
  MCP server — never guess locators from memory or a screenshot.
- Re-read this repo's `CLAUDE.md`, specifically "Conventions to follow" and "Adding things", so
  any rule changes since this skill was last touched are picked up.
- Re-read `src/pages/base_page.py` and note every existing `_`-prefixed helper. Reuse these —
  never reimplement click/fill/assert directly.
- Read `src/utils/strings.json` and `conftest.py` so the current shape is known before editing.
- Check whether `src/pages/<name>_page.py` **or** a same-named fixture already exists in
  `conftest.py`. If either does, ask the user: overwrite, merge, or cancel.

## Inputs to collect before writing anything

1. **POM class name.** `$ARGUMENTS` if provided (e.g. `/create-pom CheckoutPage`), otherwise ask.
   Must end in `Page` and describe the page's purpose, not its position — reject `Page1`,
   `MyPage`, `TheSecondScreen` and ask for a better name.
2. **Navigation steps** to reach the page from the app's entry point. Follow them literally; if a
   step is ambiguous, stop and ask rather than guess.
3. **Auth state.** Does the page require a logged-in user? This repo already has a working
   `LoginPage` wired to `environment_configuration.ui_username`/`ui_password` and reachable via
   the `login_page` fixture — a page that needs login routes its nav steps through that fixture
   instead of requiring new auth infrastructure.
4. **Optional direct URL.** Accept it as a shortcut if the user already knows it and it's
   reachable without the nav steps.

## Step 1 — Drive the browser via Playwright MCP

- Open the app at `environment_configuration.ui_base_url` (fallback:
  `https://the-internet.herokuapp.com`).
- Execute each navigation step via Playwright MCP (`browser_navigate`, `browser_click`,
  `browser_type`, `browser_select_option`, ...). Never invent steps.
- Once on the target page, capture an accessibility snapshot (`browser_snapshot`) — every
  interactive element with its role and accessible name — and the raw DOM, to find
  `data-testid` attributes the accessibility tree hides.
- If the page has several visually distinct regions (header, side nav, main content), inspect
  each before deciding what belongs in this POM. Split into multiple POMs if the page covers
  multiple concerns.

## Step 2 — Strings

Open `src/utils/strings.json`. Under `pages.<snake_case_key>` (strip the `Page` suffix and
snake_case it — `CheckoutPage` → `pages.checkout`, `ShoppingCartPage` → `pages.shopping_cart`),
add **only genuine user-facing text**:

```json
"checkout": {
  "url_path": "/checkout",
  "page_title_heading_text": "Checkout",
  "place_order_button_accessible_name": "Place order",
  "order_confirmed_flash_fragment": "Your order is confirmed"
}
```

Labels, URL paths, accessible names, and messages go here. `.describe()` /
`element_description` strings, and any DOM-internal value (an option's `value` attribute, a
data attribute) never go here — those are either inline literals in the page file, or, if a page
needs to translate a user-visible label into an internal value, a private mapping constant in
the page file itself (see `CLAUDE.md` rule 1 and the API-client precedent of keeping internal
details as code constants, not `strings.json` entries).

Templated text needing a runtime value uses `{placeholder}` syntax, substituted with
`.replace("{placeholder}", value)` at the call site. Do not reintroduce a formatter/resolver
helper — this project deliberately has none.

## Step 3 — Extend `BasePage` only if something is missing

Before writing the POM, check which `BasePage` helpers the new page needs. If an interaction
isn't covered (`select_option`, hover, file upload, key press, a new assertion shape like
"has value"), add a new `_`-prefixed method to `src/pages/base_page.py`:

```python
def _select_option_from_dropdown(
    self, element_locator: Locator, option_label: str, element_description: str
) -> None:
    self._logger.info(f'Selecting "{option_label}" on element: {element_description}')
    element_locator.select_option(label=option_label)
```

Rules:
- Signature: `(self, element_locator: Locator, ...action-specific args..., element_description: str) -> None`.
- Actions log at `info`; assertions log at `debug` (matching every existing method in the file).
- Only web-first, auto-waiting Playwright APIs. **No** `time.sleep()`, **no**
  `locator.wait_for()` as a pre-action gate — Playwright's actions already auto-wait, and the
  existing `_assert_element_*` helpers already wait-and-retry via `expect()`.
- Full type annotations — `mypy` checks `src/` with `disallow_untyped_defs = true`.

If no new helper is needed, don't touch `BasePage`.

## Step 4 — Write the POM file

Create `src/pages/<snake_case>_page.py`. Method order is fixed: locators built in `__init__` →
atomic action methods (one user interaction each) → one composite method that chains atomics →
assertions last (page-specific ones live here, **never** on `BasePage` — see `CLAUDE.md` rule 7).

```python
from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_CHECKOUT_PAGE_STRINGS = strings["pages"]["checkout"]


class CheckoutPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._place_order_button = page.get_by_role(
            "button", name=_CHECKOUT_PAGE_STRINGS["place_order_button_accessible_name"]
        ).describe("Place order button")
        # ... remaining locators, built using the Locator priority order above

    def click_place_order_button(self) -> None:
        self._click_on_element(self._place_order_button, "Place order button")

    # one composite per meaningful flow, chaining atomics — see LoginPage.login for the pattern

    def assert_order_confirmed(self) -> None:
        ...  # page-specific assertion, built from a BasePage helper
```

Checklist — verify every item before saving:

| # | Rule | Check |
|---|---|---|
| 1 | No hard-coded *page* text | User-facing text from `strings.pages.<key>.*`; `.describe()`/descriptions stay inline |
| 2 | Uses `BasePage` helpers | Every action/assertion goes through a `_`-prefixed `BasePage` method |
| 3 | Locator priority | Semantic first, `get_by_test_id` last, never CSS/XPath |
| 4 | `.describe()` on every locator | Constructor-level and any inline/dynamic locators |
| 5 | Small atomic + composite methods | One user action per atom; at least one composite where it helps |
| 6 | Informative names | `click_checkout_cta_button`, `assert_cart_is_empty` — never `click()`/`check()` |
| 7 | Reachable via fixture | See Step 5 |
| 8 | Purposeful class name | Ends in `Page`, describes the page's role, not its position |
| 9 | Lives under `src/pages/` | `src/pages/<name>_page.py` |
| 10 | No implicit waits | Web-first assertions only; no `time.sleep()`/`wait_for()` pre-action gates |
| 11 | Assertions at the bottom | After atomic + composite actions |
| 12 | Fully typed | Every method fully annotated |

## Step 5 — Register a `conftest.py` fixture

```python
@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)
```

Fixture name = file base name (`checkout_page`) — a direct mapping since everything is already
snake_case. A test reaches the POM only through the fixture parameter
(`def test_x(checkout_page: CheckoutPage) -> None:`). Never `CheckoutPage(page)` inside a test
body — that is the anti-pattern this fixture exists to prevent.

## Step 6 — Verify

All three must pass before this skill is done:

```bash
ruff check .
mypy
pytest --collect-only -q
```

`pytest --collect-only` won't create tests for the new POM — it confirms the suite still
collects cleanly and nothing existing broke.

## Step 7 — Report back

- **Class + file path.**
- **Locator strategy counts** — `get_by_role: N`, `get_by_label: N`, `get_by_placeholder: N`,
  `get_by_text: N`, `get_by_title: N`, `get_by_test_id: N`, chained/filtered: N. A raw
  `page.locator()` should never occur — if it did, that's a bug in this run, not a "flag as
  tech debt" item.
- **Strings added** — the new keys under `strings.pages.<key>`.
- **New `BasePage` helper**, if any, and what it wraps. Otherwise: "no BasePage change needed".
- **Fixture name** added to `conftest.py`.
- **`ruff` / `mypy` / `pytest --collect-only` status** — pass/fail, with an error summary on
  failure.
- **Best-practice sanity check** — one line each: locators are user-facing, no implicit waits,
  all assertions are web-first, any aggregate check is split into separate methods (never a
  soft-assertion shortcut — this repo has none).

## Anti-patterns — refuse and explain

Stop and explain rather than producing the POM if the request would need any of these:

1. A test importing `Page` or building a locator directly, instead of going through a POM
   fixture.
2. A POM method performing more than one user action — split into atoms + one composite.
3. `time.sleep(...)` or `locator.wait_for(...)` as a pre-action gate. Every legitimate reason to
   reach for either is already covered: Playwright's actions auto-wait, and the web-first
   assertion helpers already wait-and-retry via `expect()`. A fixed `time.sleep()` has no
   legitimate use here at all. (Waiting on a non-locator condition — a URL change, a network
   response — is a different API, `page.wait_for_url`/`wait_for_response`, and would become a
   new `BasePage` helper per Step 3, not an exception to this rule.)
4. A manual `assert locator.is_visible()` instead of `_assert_element_is_visible` — it doesn't
   retry and will flake.
5. Hard-coded page text instead of `strings.json` (element descriptions are the documented
   exception above).
6. `page.locator(css_or_xpath)` when a semantic or test-id locator is possible.
7. A locator built from a CSS class, component name, or framework-generated id.
8. A third-party call asserted on directly from a POM — mock it with `page.route()` at the test
   level; the POM stays third-party-agnostic.
9. A class name that doesn't end in `Page`, or that describes position instead of purpose.
10. A new POM with no matching `conftest.py` fixture.
11. Reintroducing a string-formatting/resolver helper — use `.replace("{placeholder}", value)`
    at the call site.

## Example invocation

```
/create-pom CheckoutPage
```

The skill then asks:

> What are the exact navigation steps to reach the checkout page from the app's entry point?
> Does this page require a logged-in user?

...and proceeds through Steps 1–7.
````

- [ ] **Step 2: Confirm the frontmatter has exactly the expected keys**

Run: `grep -E '^(name|description|argument-hint|disable-model-invocation|allowed-tools):' .claude/skills/create-pom/SKILL.md | wc -l`
Expected: `5`

- [ ] **Step 3: Confirm every required section is present**

Run: `grep -c '^## ' .claude/skills/create-pom/SKILL.md`
Expected: `12` — Locator priority, Preflight, Inputs to collect, Step 1 through Step 7 (7
headings), Anti-patterns, Example invocation.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/create-pom/SKILL.md
git commit -m "Add create-pom skill for Python/pytest Page Objects

Ports the TypeScript create-pom skill's intent to this repo's actual
conventions: sync Playwright, semantic-first locators, conftest.py
fixtures, and inline element descriptions per CLAUDE.md rule 1."
```

---

### Task 3: Validate the skill end-to-end against a real page

This task requires a Claude Code session with Playwright MCP available — it exercises the skill
built in Task 2 by actually running it, not by re-deriving its logic.

**Files:**
- Create: `src/pages/dropdown_page.py`
- Modify: `src/pages/base_page.py` (new helpers)
- Modify: `src/utils/strings.json`
- Modify: `conftest.py`
- Test: `tests/ui/test_example_dropdown.py`

**Interfaces:**
- Consumes: the `create-pom` skill from Task 2; `BasePage` from Task 1/existing code.
- Produces: `DropdownPage.__init__(self, page: Page) -> None`, `DropdownPage.open(self) -> None`,
  `DropdownPage.select_dropdown_option(self, option_label: str) -> None`,
  `DropdownPage.assert_dropdown_option_is_selected(self, expected_label: str) -> None`; a
  `dropdown_page` fixture returning `DropdownPage`; `BasePage._select_option_from_dropdown` and
  `BasePage._assert_element_has_value`.

The target page, `https://the-internet.herokuapp.com/dropdown`, was fetched and confirmed to be:

```html
<div class="example">
  <h3>Dropdown List</h3>
  <select id="dropdown">
    <option value="" disabled="disabled" selected="selected">Please select an option</option>
    <option value="1">Option 1</option>
    <option value="2">Option 2</option>
  </select>
</div>
```

One native `<select>`, no label, no `data-testid`. Playwright maps a native `<select>` to ARIA
role `combobox`, so `page.get_by_role("combobox")` is the correct (and only necessary) locator —
this is exactly the kind of page that proves the skill's semantic-first priority order actually
resolves correctly when no test id exists.

- [ ] **Step 1: Invoke the skill**

In a Claude Code session on this branch, run:

```
/create-pom DropdownPage
```

When asked for navigation steps, answer: "Navigate directly to
https://the-internet.herokuapp.com/dropdown — no login, no prior steps." When asked about auth
state, answer: "Not required."

- [ ] **Step 2: Check the output against this checklist**

- [ ] `src/pages/dropdown_page.py` exists, class `DropdownPage(BasePage)`.
- [ ] The `<select>` locator uses `get_by_role("combobox")` — not a CSS id selector, not
      `get_by_label` (there is no label on this page).
- [ ] `strings.json` gained a `pages.dropdown` block with only `url_path` and the option's
      visible label text — no `.describe()` strings, no raw `value="1"` attribute.
- [ ] `src/pages/base_page.py` gained a `_select_option_from_dropdown`-equivalent helper, since
      no existing helper handles `<select>` interaction.
- [ ] `conftest.py` gained a `dropdown_page` fixture.
- [ ] Every locator ends with `.describe(...)`.
- [ ] Methods are ordered: locators in `__init__` → actions → assertions.

If any item fails, the exact code doesn't need to match what follows below byte-for-byte — but
if the *shape* is wrong (e.g., a CSS selector was used, or the option value ended up in
`strings.json`), fix the wording in `.claude/skills/create-pom/SKILL.md` that caused the gap,
delete the generated files, and re-run Step 1 until the checklist passes.

- [ ] **Step 3: Reconcile against this reference implementation**

If the skill's output is checklist-compliant but named things differently, rename to match this
reference so Step 4's test lines up (or adjust the test in Step 4 to match the skill's naming —
either is fine as long as the two agree):

`src/pages/dropdown_page.py`:

```python
from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.strings import strings

_DROPDOWN_PAGE_STRINGS = strings["pages"]["dropdown"]

_OPTION_VALUES_BY_LABEL: dict[str, str] = {
    "Option 1": "1",
    "Option 2": "2",
}


class DropdownPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._dropdown_select = page.get_by_role("combobox").describe("Dropdown select")

    def open(self) -> None:
        self._navigate_to_url_path(_DROPDOWN_PAGE_STRINGS["url_path"])

    def select_dropdown_option(self, option_label: str) -> None:
        self._select_option_from_dropdown(self._dropdown_select, option_label, "Dropdown select")

    def assert_dropdown_option_is_selected(self, expected_label: str) -> None:
        expected_value = _OPTION_VALUES_BY_LABEL[expected_label]
        self._assert_element_has_value(self._dropdown_select, expected_value, "Dropdown select")
```

Add to `src/pages/base_page.py` (alongside the other action/assertion methods, in their
respective sections):

```python
    def _select_option_from_dropdown(
        self, element_locator: Locator, option_label: str, element_description: str
    ) -> None:
        self._logger.info(f'Selecting "{option_label}" on element: {element_description}')
        element_locator.select_option(label=option_label)
```

```python
    def _assert_element_has_value(
        self, element_locator: Locator, expected_value: str, element_description: str
    ) -> None:
        self._logger.debug(
            f'Asserting element "{element_description}" has value: {expected_value}'
        )
        expect(element_locator, element_description).to_have_value(expected_value)
```

Add to `src/utils/strings.json`, under `"pages"`:

```json
    "dropdown": {
      "url_path": "/dropdown",
      "option_one_label": "Option 1"
    }
```

Add to `conftest.py`:

```python
from src.pages.dropdown_page import DropdownPage
```

```python
@pytest.fixture
def dropdown_page(page: Page) -> DropdownPage:
    return DropdownPage(page)
```

- [ ] **Step 4: Write the real test**

Create `tests/ui/test_example_dropdown.py`:

```python
from src.pages.dropdown_page import DropdownPage
from src.utils.strings import strings

_DROPDOWN_PAGE_STRINGS = strings["pages"]["dropdown"]


def test_selecting_option_one_updates_dropdown_value(dropdown_page: DropdownPage) -> None:
    dropdown_page.open()

    dropdown_page.select_dropdown_option(_DROPDOWN_PAGE_STRINGS["option_one_label"])

    dropdown_page.assert_dropdown_option_is_selected(_DROPDOWN_PAGE_STRINGS["option_one_label"])
```

- [ ] **Step 5: Run the new test**

Run: `pytest tests/ui/test_example_dropdown.py -v`
Expected: `1 passed`.

- [ ] **Step 6: Lint, typecheck, and confirm nothing else broke**

Run: `ruff check . && mypy && pytest --collect-only -q`
Expected: `ruff` and `mypy` exit `0`; `pytest --collect-only` lists all tests (including the new
one) with no collection errors.

- [ ] **Step 7: Commit**

```bash
git add src/pages/dropdown_page.py src/pages/base_page.py src/utils/strings.json conftest.py tests/ui/test_example_dropdown.py
git commit -m "Add DropdownPage as a create-pom skill validation example

Exercises the create-pom skill end-to-end against a page with no
data-testid or label, proving the semantic-locator priority order and
the BasePage-extension step both work as documented."
```
