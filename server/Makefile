PYTHON ?= python
.PHONY: test run install
install:
	$(PYTHON) -m pip install -r requirements.lock
test:
	$(PYTHON) -m pytest tests -q
run:
	$(PYTHON) server.py
