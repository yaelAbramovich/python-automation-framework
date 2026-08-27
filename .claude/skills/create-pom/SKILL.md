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
