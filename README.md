# JED-2048

Playwright-powered 2048 bot with computer vision and pluggable strategies. This repo is a cleaned fork of an educational 2048 bot platform, migrated to Playwright-only automation with a streamlined toolchain.

## Features
- Playwright browser control (Chromium/Firefox/WebKit)
- Vision pipeline using OpenCV/Pillow/Numpy
- Heuristic strategy with tunable weights; extensible algorithms folder
- Production utilities: error handling, performance monitor
- Tools for verification, diagnosis, and quick runs

## Quick Start
- Setup
  - `make setup`  (creates venv, installs deps, installs Playwright browsers)
- Run visible validation game
  - `make run`    (opens a visible browser and runs a game)
- Run a 16-move visible sample
  - `make run16`
- Tests (selective)
  - `make test`   (note: some tests require manual/GUI interaction)

If Playwright is missing in your venv:
- `pip install playwright && playwright install`

## Project Structure
- `core/` – vision, strategy, and Playwright controllers
- `algorithms/` – strategy implementations and registry
- `production/` – error handling and monitoring utilities
- `tools/` – verification scripts (Playwright-based)
- `docs/` – integration, troubleshooting, and project index
- `scripts/` – helpers (index generation, run 16 moves)

## Notes
- Selenium and webdriver-manager have been removed; see `docs/DEPRECATIONS.md`.
- For setup details, see `PLAYWRIGHT_SETUP_INSTRUCTIONS.md`.

## License
TBD
