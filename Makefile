.PHONY: test run

test:
	pytest

run:
	streamlit run app/streamlit_app.py
