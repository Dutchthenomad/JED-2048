# Project Index: 2048-demo

Path: `/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo`

This project contains a Python-based automation and vision system for the 2048 game, using Playwright for browser control and OpenCV/Pillow/Numpy for image processing. It includes multiple algorithm strategies, a production harness, and test suites.

## Quick Stats

- Files indexed: 192
- By type: 76 Python, 7 Markdown, 1 JSON, 1 TXT, 1 LOG, 106 PNG

## Dependencies (from requirements.txt)

- mss>=7.0.0
- pillow>=9.0.0
- numpy>=1.24.0
- opencv-python>=4.8.0
- click>=8.1.0
- pytest>=7.4.0
- playwright>=1.55.0
- psutil>=5.9.0

## Top-Level Files

- `complete_2048_bot.py` – Full bot entry; likely orchestrates capture, strategy, and control.
- `enhanced_2048_bot.py` – Enhanced bot variant with improved heuristics/vision.
- `working_2048_bot.py` – A baseline/minimal working bot.
- `run_visible_bot.py` – Launches a visible browser session for manual observation.
- `student_platform.py` – Student-facing entrypoints/integration layer.
- `leaderboard_system.py` – Leaderboard aggregation and scoring utilities.
- `requirements.txt` – Python dependencies.
- `BROWSER_SETUP.md`, `PLAYWRIGHT_SETUP_INSTRUCTIONS.md`, `README_PRODUCTION.md`, `VALIDATION_GUIDE.md` – setup/usage guides.

## Key Directories

- `core/` – Core engine modules
  - `vision.py`, `canonical_vision.py`, `improved_vision.py` – Tile/grid detection and image processing.
  - `strategy.py`, `game_bot.py` – Move selection and bot orchestration.
  - `playwright_controller.py`, `browser_controller.py` – Playwright-based browser control.
  - `capture.py` – Screen/window capture helpers.

- `algorithms/` – Strategy implementations and management
  - `basic/`, `heuristic/`, `minimax/`, `reinforcement_learning/`, `deep_rl/`, `student_submissions/` – Strategy families and experiments.
  - `base_algorithm.py`, `algorithm_manager.py` – Shared interfaces and registry.

- `production/` – Runtime hardening and ops
  - `error_handler.py`, `performance_monitor.py`, `__init__.py` – Production wrappers and metrics.

- `config/`
  - `production.json` – Environment/configuration defaults for production runs.

- `tools/` – Utility CLIs and diagnostics
  - Examples: `verify_browser_setup.py`, `test_playwright_compatibility.py`, `validate_vision.py`, `test_strategy.py`, `run_bot.py`, `train_vision.py`, `retrain_vision.py`, `analyze_gameover.py`.

- `tests/` – Unit/integration tests
  - `test_integration.py`, `test_capture.py`, `test_bot_integration.py`, `test_vision.py`, `__init__.py`.

- `docs/` – Guides and runbooks
  - `INTEGRATION_GUIDE.md`, `PRODUCTION_STRUCTURE.md`, `TROUBLESHOOTING.md`, `PROJECT_INDEX.md` (this file).

- `validation_data/` – Captured images and JSON datasets for validation and training.
- `debug_archive/` – Debug screenshots and traces.
- `logs/`, `reports/` – Runtime logs and reports.

## Test Layout

- Location: `tests/` with pytest-based tests; additional ad hoc tests live under `tools/`.
- Run: `pytest -q` (ensure Playwright/Chrome setup is completed per setup docs).

## How To Run Locally

1) Create venv and install deps

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Verify browser automation setup

```
python tools/verify_systems.py
python tools/verify_browser_setup.py
python tools/test_playwright_compatibility.py
```

3) Try a visible bot run

```
python run_visible_bot.py
```

4) Run tests

```
pytest -q
```

## Notes

- Large image assets live under `debug_archive/` and `validation_data/`; these are excluded from the file count where relevant.
- For production-hardening or metrics, see `production/` and `README_PRODUCTION.md`.
- For detailed integration steps and troubleshooting, see `docs/` and the setup READMEs.
