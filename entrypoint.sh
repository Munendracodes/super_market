#!/bin/sh
set -e

echo "⏳ Waiting for MySQL to be ready..."
until nc -z "$MYSQL_HOST" "$MYSQL_PORT"; do
  sleep 1
done
echo "✅ MySQL is up!"

echo "🚀 Running Alembic migrations..."
alembic upgrade head

echo "✅ Starting FastAPI with Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
