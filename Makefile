.PHONY: setup migrate run test lint clean

setup:
	cp .env.example .env
	docker compose up -d db redis
	sleep 5
	python manage.py migrate
	python manage.py createsuperuser

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	docker compose up

run-dev:
	docker compose -f compose.yml -f docker-compose.override.yml up

test:
	pytest

lint:
	ruff check .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
