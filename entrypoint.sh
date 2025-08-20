#!/bin/sh
set -e

# Start FastAPI
echo "✅ Starting FastAPI with Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000