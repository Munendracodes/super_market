#!/bin/sh
set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD || echo "dev")
echo "🌍 Current branch: $BRANCH"

# ============================
# Wait for Redis
# ============================
echo "⏳ Waiting for Redis..."
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  echo "   Redis not ready at $REDIS_HOST:$REDIS_PORT, retrying in 2s..."
  sleep 2
done
echo "✅ Redis is up!"

# ============================
# Run Alembic (optional)
# ============================
if [ "$BRANCH" = "release" ]; then
  echo "📦 Running Alembic migrations for release..."
  alembic upgrade head
fi

# ============================
# Start FastAPI
# ============================
echo "✅ Starting FastAPI with Uvicorn..."
if [ "$BRANCH" = "main" ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
