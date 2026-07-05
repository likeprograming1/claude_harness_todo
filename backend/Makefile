.PHONY: dev test lint typecheck

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check . && ruff format --check .

typecheck:
	mypy app/
