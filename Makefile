.PHONY: test lint format quality install-hooks run coverage

test:
	python -m pytest -q

lint:
	python -m ruff check src/ tests/

format:
	python -m ruff check src/ tests/ --fix

coverage:
	python -m pytest --cov --cov-report=term-missing -q

quality: lint test

install-hooks:
	./scripts/install-hooks.sh

run:
	streamlit run app/streamlit_app.py
