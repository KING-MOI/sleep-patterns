PY ?= python

.PHONY: data charts test lint notebooks

data:
	$(PY) data/generate.py

charts:
	$(PY) -m sleep_patterns.report

test:
	$(PY) -m pytest -q

lint:
	ruff check .
	ruff format --check .

notebooks:
	jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
