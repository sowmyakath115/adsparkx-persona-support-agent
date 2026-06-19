.PHONY: install ingest chat streamlit test

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -e .

ingest:
	python -m support_agent.ingest

chat:
	python -m support_agent.cli

streamlit:
	streamlit run src/support_agent/streamlit_app.py

test:
	pytest -q
