#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Simple wait loop - in production you might want a more sophisticated check
sleep 2

echo "Running database migrations..."
cd /app
alembic -c /db/alembic.ini upgrade head

echo "Running seed script..."
python /db/seed.py

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir /app
