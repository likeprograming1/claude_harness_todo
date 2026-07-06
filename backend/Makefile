.PHONY: install install-dev dev test lint typecheck clean docker-up docker-down docker-logs

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ --asyncio-mode=auto -v

lint:
	ruff check app/ && ruff format --check app/

typecheck:
	mypy app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; \
	true

docker-up:
	docker compose -f ../docker-compose.yml up -d --build

docker-down:
	docker compose -f ../docker-compose.yml down

docker-logs:
	docker compose -f ../docker-compose.yml logs -f backend
