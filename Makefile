.PHONY: test lint typecheck format quality install-hooks run coverage

test:
	python -m pytest -q

lint:
	python -m ruff check src/ tests/ app/

typecheck:
	python -m mypy src

format:
	python -m ruff check src/ tests/ app/ --fix

coverage:
	python -m pytest --cov --cov-report=term-missing -q

quality: lint typecheck test

install-hooks:
	./scripts/install-hooks.sh

run:
	streamlit run app/streamlit_app.py
