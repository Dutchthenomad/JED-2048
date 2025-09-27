VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip

.PHONY: setup run test fmt index

setup:
	python -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	. $(VENV)/bin/activate && $(PY) -c "from playwright.sync_api import sync_playwright; print('Playwright installed')" || $(PIP) install playwright
	. $(VENV)/bin/activate && playwright install

run:
	. $(VENV)/bin/activate && $(PY) run_visible_bot.py

run16:
	. $(VENV)/bin/activate && $(PY) scripts/run_bot_16.py

test:
	. $(VENV)/bin/activate && pytest -q

fmt:
	@echo "No formatter configured. Install black/isort if desired."

index:
	. $(VENV)/bin/activate && $(PY) scripts/generate_index.py --out docs/PROJECT_INDEX.json
