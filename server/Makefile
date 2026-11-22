.PHONY: test run install
install:
	cd .. && uv sync --locked --group dev
test:
	cd .. && uv run --locked pytest tests -q
run:
	cd .. && uv run --locked python main.py
