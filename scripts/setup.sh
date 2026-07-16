#!/bin/bash
set -e

cp .env.example .env

docker compose up -d db redis

echo "Waiting for database..."
sleep 5

docker compose exec db psql -U appointments -c "CREATE DATABASE appointments;" || true
docker compose exec db psql -U appointments -c "CREATE USER appointments WITH PASSWORD 'change-me';" || true

python manage.py migrate
python manage.py createsuperuser

docker compose up -d
