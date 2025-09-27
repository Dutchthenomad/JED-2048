# Deprecations and Removals (Playwright Migration)

This fork removes Selenium-based controllers and standardizes on Playwright.

## Removed
- `core/chrome_browser.py` (Selenium Chrome controller)
- `core/enhanced_browser.py` (Selenium Firefox/Snap enhancements)
- `tools/test_chrome_setup.py` (Selenium Chrome setup test)
- `tools/fix_browser_setup.py` (Selenium/Snap Firefox fixer)
- Dependencies: `selenium`, `webdriver-manager` (removed from `requirements.txt`)

## Replaced
- `core/browser_controller.py` now delegates to `core/playwright_controller.py` with the same API.
- `GameAction` values now use Playwright key names (`ArrowUp`, etc.) instead of Selenium `Keys`.

## Candidates To Update or Remove Next
- `tools/diagnose_browser.py` (Selenium imports present)
- `tools/simple_browser_test.py` (Selenium imports present)
- `tools/verify_systems.py` (Selenium imports present in optional branches)

These tools should be rewritten to use `core/browser_controller.py` or `core/playwright_controller.py`, or removed if redundant with existing Playwright tests (`tools/test_browser.py`, `tools/verify_browser_setup.py`, `tools/test_playwright_compatibility.py`).

## Documentation
- `BROWSER_SETUP.md` contains Firefox/Selenium guidance; prefer `PLAYWRIGHT_SETUP_INSTRUCTIONS.md`. Update or annotate as legacy.

