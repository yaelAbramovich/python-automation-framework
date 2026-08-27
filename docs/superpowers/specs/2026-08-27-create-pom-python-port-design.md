# create-pom: porting the Playwright POM-generator skill to Python

**Status:** approved, pending implementation plan
**Branch:** `implement-pom-skill`

## Context

A Claude Code skill named `create-pom` already exists for a TypeScript + `@playwright/test`
framework. It drives Playwright MCP to inspect a live page, then writes a new Page Object Model
following that repo's conventions: locators prioritizing `getByTestId`, all text (including
`.describe()` strings) centralized in `strings.json`, async/await throughout, and every POM
registered as a fixture in a `fixtures.ts` file.

This repo (`python-automation-framework`) is a different framework: sync `playwright.sync_api`,
pytest, `ruff`/`mypy` instead of `eslint`/`tsc`, and its own documented conventions in
`CLAUDE.md`. The goal is a `create-pom` skill for *this* repo that produces POMs indistinguishable
from ones a careful human maintainer would write here — which means porting intent, not syntax.
Several TS-skill rules don't apply as-is and needed explicit decisions (recorded below).

## Decisions

These were the open questions, resolved with the user before writing this spec:

1. **Locator priority is semantic-first, `get_by_test_id` last** — `get_by_role` → `get_by_label`
   → `get_by_placeholder` → `get_by_text` → `get_by_title` → `get_by_test_id` → `.filter(...)`
   chaining → stop and ask for a locator hook. This matches Playwright's own best-practice order
   and the repo's only existing page (`LoginPage`, which never uses a test id). The TS skill's
   test-id-first rule does not carry over.

2. **New POMs get a pytest fixture in `conftest.py`.** Test preparation belongs in fixtures. Every
   new POM gets a fixture there (not a separate fixtures file — pytest fixtures conventionally
   live in `conftest.py`, and this repo's already does). Direct instantiation
   (`SomePage(page)`) inside a test body becomes the anti-pattern, replacing the TS skill's
   `fixtures.ts`-registration rule.

3. **`LoginPage` is migrated for consistency.** Introducing fixtures changes the established
   pattern, so as part of this work `conftest.py` gains a `login_page` fixture and
   `tests/ui/test_example_login.py` is updated to use it — the repo does not end up with two
   conflicting patterns (fixture-based for new pages, direct instantiation for the one existing
   page).

4. **No soft-assertion concept.** Playwright's sync API has no `expect.soft()` equivalent, and
   this repo has no soft-assertion plugin (e.g. `pytest-check`). Aggregate checks are always
   multiple small `assert_*` methods called in sequence — matching the repo's existing rule that
   page-specific assertions stay small and specific. No new dependency is introduced.

5. **The skill lives at `.claude/skills/create-pom/SKILL.md`.** No project skill folder exists
   yet in this repo; this is the first one. It uses the same frontmatter shape as the TS original
   (`name`, `description`, `argument-hint`, `disable-model-invocation`, `allowed-tools`).

6. **Element-description strings stay inline, not centralized.** This isn't a new decision so
   much as an existing repo rule the port must respect: `CLAUDE.md` rule 1 explicitly excludes
   `.describe()` / `element_description` text from `strings.json` — "API paths and log/description
   text stay out of it... those live on the client/page code itself." Only genuine user-facing
   page text (labels, URL paths, accessible names, messages) goes in `strings.json`. This is the
   one place the port changes an actual *rule* from the TS skill, not just its syntax — the TS
   version centralized both into a `strings.json.descriptions` sub-object. Confirmed with the user
   during design review.

## Skill behavior

### Frontmatter

```yaml
name: create-pom
description: Generate a pytest/Playwright Page Object for this repo. Drives Playwright MCP to
  inspect the target page in a live browser, writes the POM under src/pages/, adds user-facing
  text to src/utils/strings.json, extends BasePage if a helper is missing, and registers the POM
  as a fixture in conftest.py. Invoked explicitly by the user — never auto-trigger.
argument-hint: [PageClassName]
disable-model-invocation: true
allowed-tools: Bash(ruff check .), Bash(mypy), Bash(pytest --collect-only)
```

Invoked as `/create-pom CheckoutPage`.

### Preflight (every invocation)

- Confirm Playwright MCP tools are reachable; if not, stop and tell the user to start the MCP
  server rather than guessing locators from memory.
- Re-read `CLAUDE.md`'s "Conventions to follow" and "Adding things" sections, so rule updates
  since the skill was written are picked up.
- Re-read `src/pages/base_page.py` and note every existing `_`-prefixed helper — the POM must
  reuse these, never reimplement click/fill/assert directly.
- Read `src/utils/strings.json` and `conftest.py` so the current shape is known before editing.
- Check whether `src/pages/<name>_page.py` **or** a same-named fixture already exists in
  `conftest.py`. If either does, ask the user: overwrite, merge, or cancel.

### Inputs to collect

1. **POM class name** — from `$ARGUMENTS` if given, else ask. Must end in `Page` and describe the
   page's purpose, not its position (`Page1`, `TheSecondScreen` get rejected with a request for a
   better name).
2. **Navigation steps** to reach the page from the app's entry point, followed literally; any
   ambiguous step stops the skill to ask rather than guess.
3. **Auth state** — does the page require a logged-in user? Unlike the TS repo (which had no
   shared login setup at all), this repo already has a working `LoginPage` wired to
   `environment_configuration.ui_username`/`ui_password`. A page requiring login routes its nav
   steps through the `login_page` fixture (see Decision 3) rather than raising a blocking
   question about missing infrastructure.
4. **Optional direct URL** — accepted as a shortcut if the user already knows it and it's
   reachable without the nav steps.

### Step 1 — Drive the browser via Playwright MCP

Open the app at `environment_configuration.ui_base_url` (fallback:
`https://the-internet.herokuapp.com`, the same demo site `LoginPage` already targets). Execute
each navigation step via Playwright MCP (`browser_navigate`, `browser_click`, `browser_type`,
`browser_select_option`, ...) — never inventing steps. Once on the target page, capture an
accessibility snapshot (`browser_snapshot`) and the raw DOM (for `data-testid` attributes the a11y
tree hides). Pages with multiple distinct regions get inspected region by region and split into
multiple POMs if they cover multiple concerns.

### Step 2 — Locator selection

For each interactive element, walk this list in order and stop at the first that works:

1. `page.get_by_role("role", name="Accessible Name")`
2. `page.get_by_label("label text")`
3. `page.get_by_placeholder("placeholder text")`
4. `page.get_by_text("visible text")`
5. `page.get_by_title("title text")`
6. `page.get_by_test_id("value")`
7. Chain + filter one of the above — `.filter(has_text="...")`, `.filter(has=child_locator)`,
   or parent-locator chaining — for repeating structures (lists, tables, cards) or scoping into a
   region. Preferred over any deeper selector.
8. **Never `page.locator(css_or_xpath)`.** If nothing above works, stop and ask the user whether a
   `data-testid` (or role/label) can be added to the element. This repo's README forbids CSS/XPath
   outright — there is no "last resort, flag as tech debt" fallback like the TS skill had.

When unsure, `playwright codegen <url>` (the pip-installed CLI, which emits sync Python by
default) is the tie-breaker.

Every locator ends with `.describe("Human-readable element name")` — a literal string, matching
Decision 6.

### Step 3 — Strings

Open `src/utils/strings.json`. Under `pages.<snake_case_key>` (strip the `Page` suffix and
snake_case it: `CheckoutPage` → `pages.checkout`, `ShoppingCartPage` → `pages.shopping_cart`), add
only genuine user-facing text:

```json
"checkout": {
  "url_path": "/checkout",
  "page_title_heading_text": "Checkout",
  "place_order_button_accessible_name": "Place order",
  "order_confirmed_flash_fragment": "Your order is confirmed"
}
```

No `descriptions` sub-object (Decision 6). Templated text needing a runtime value uses
`{placeholder}` syntax and is substituted with `.replace("{placeholder}", value)` at the call
site — no resolver/formatter helper is reintroduced.

### Step 4 — Extend `BasePage` only if needed

If an interaction isn't covered (`select_option`, `hover`, file upload, key press), add a new
`_`-prefixed method to `src/pages/base_page.py`:

```python
def _select_option_from_dropdown(
    self, element_locator: Locator, option_value: str, element_description: str
) -> None:
    self._logger.info(f'Selecting "{option_value}" on element: {element_description}')
    element_locator.select_option(option_value)
```

Signature: `(self, element_locator: Locator, ...action-specific args..., element_description:
str) -> None`. Actions log at `info`, assertions at `debug`. No `time.sleep()`, no
`locator.wait_for()` as a pre-action gate — see Anti-patterns. If no new helper is needed,
`BasePage` isn't touched.

### Step 5 — Write the POM file

`src/pages/<snake_case>_page.py`:

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
        # ... remaining locators, built in Step 2's priority order

    # Atomic actions — one user interaction per method
    def click_place_order_button(self) -> None:
        self._click_on_element(self._place_order_button, "Place order button")

    # Composite actions — compose atomics into reusable flows
    def fill_shipping_details_and_place_order(self, ...) -> None:
        ...

    # Assertions — always last, page-specific ones live here (never on BasePage)
    def assert_order_confirmed(self) -> None:
        ...
```

Method order is fixed: locators in `__init__` → atomic actions → composite actions → assertions.
Rule mapping (each verified before saving):

| # | Rule | Enforcement |
|---|---|---|
| 1 | No hard-coded *page* text | User-facing text from `strings.pages.<key>.*`; element descriptions stay inline (Decision 6) |
| 2 | Uses `BasePage` helpers | Every action/assertion goes through `_click_on_element`, `_fill_element_with_text`, `_assert_element_is_visible`, etc. |
| 3 | Locator priority | Per Step 2 — semantic first, `get_by_test_id` last, never CSS/XPath |
| 4 | `.describe()` on every locator | Constructor and any inline/dynamic locators |
| 5 | Small atomic + composite methods | One user action per atom; at least one composite |
| 6 | Informative names | `click_checkout_cta_button`, `assert_cart_is_empty` — never `click()`/`check()` |
| 7 | Reachable via fixture | See Step 6 |
| 8 | Purposeful class name | Ends in `Page`, describes the page's role |
| 9 | Lives under `src/pages/` | `src/pages/<name>_page.py` |
| 10 | No implicit waits | Web-first assertions only; no `time.sleep()`/`wait_for()` pre-action gates |
| 11 | Assertions at the bottom | After atomic + composite actions |
| 12 | Fully typed | Every method has full type annotations — `mypy` checks `src/` with `disallow_untyped_defs = true` |

### Step 6 — Register a `conftest.py` fixture

```python
@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)
```

Fixture name = file base name (`checkout_page`) — a direct 1:1 mapping since everything is already
snake_case. A test reaches the POM only via the fixture parameter
(`def test_x(checkout_page: CheckoutPage) -> None:`); never `CheckoutPage(page)` inside a test
body.

As part of this port (Decision 3): add a `login_page` fixture to `conftest.py` and update
`tests/ui/test_example_login.py` to use it instead of instantiating `LoginPage` directly.

### Step 7 — Verify

Must all pass before the skill is done:

```bash
ruff check .
mypy
pytest --collect-only -q
```

`pytest --collect-only` confirms the suite still collects cleanly and nothing existing broke — it
doesn't create tests for the new POM.

### Step 8 — Report back

- **Class + file path**
- **Locator strategy counts** — `get_by_role: N`, `get_by_label: N`, `get_by_placeholder: N`,
  `get_by_text: N`, `get_by_title: N`, `get_by_test_id: N`, chained/filtered: N. Any raw
  `page.locator()` should never occur — if it somehow did, that's a bug in the skill's own
  execution, not a reportable "tech debt" item (see Step 2).
- **Strings added** — new keys under `strings.pages.<key>`
- **New `BasePage` helper**, if any, and what it wraps
- **Fixture name** added to `conftest.py`
- **`ruff`/`mypy`/`pytest --collect-only` status** — pass/fail with error summary if failed
- **Best-practice sanity check** — locators are user-facing, no implicit waits, all assertions
  are web-first, aggregate checks are split into separate methods

## Anti-patterns — refuse and explain

1. A test importing `Page` or building a locator directly, instead of going through a POM fixture.
2. A POM method performing more than one user action — split into atoms + one composite.
3. `time.sleep(...)` or `locator.wait_for(...)` as a pre-action gate. Every legitimate reason to
   reach for either is already covered elsewhere: Playwright's actions auto-wait for
   actionability before running, and the web-first assertion helpers (`_assert_element_is_visible`
   etc.) already wait-and-retry via `expect()`. A fixed `time.sleep()` has no legitimate use case
   in this framework at all. (Waiting on a non-locator condition — a URL change, a network
   response — uses a different API, `page.wait_for_url`/`wait_for_response`, and isn't what this
   rule targets; that need becomes a new `BasePage` helper per Step 4, not an exception here.)
4. A manual `assert locator.is_visible()` instead of `_assert_element_is_visible` — doesn't retry,
   will flake.
5. Hard-coded page text instead of `strings.json` (element descriptions are the documented
   exception — Decision 6).
6. `page.locator(css_or_xpath)` when a semantic or test-id locator is possible.
7. A locator built from a CSS class, component name, or framework-generated id.
8. A third-party call asserted on directly from a POM — mock with `page.route()` at the test
   level; the POM stays third-party-agnostic.
9. A class name that doesn't end in `Page`, or that describes position instead of purpose.
10. A new POM with no matching `conftest.py` fixture (Decision 2).
11. Reintroducing a string-formatting/resolver helper — use `.replace("{placeholder}", value)` at
    the call site.

## Out of scope

- API client generation (`BaseApiClient`) — this skill only covers UI Page Objects.
- A `storageState`-equivalent auth setup project — the existing `LoginPage`-via-fixture path is
  sufficient for now; revisit if a page's auth needs outgrow it.
- Adding `pytest-check` or any other soft-assertion dependency (Decision 4).
