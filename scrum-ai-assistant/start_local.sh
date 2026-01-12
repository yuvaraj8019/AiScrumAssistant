#!/bin/bash


# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down..."
    kill $CELERY_PID
    # Don't kill redis as it might be system service, but if we started it...
    # For now, just kill celery.
    exit
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting Scrum AI Assistant..."

# Ensure Redis is running
if ! nc -z localhost 6379; then
    echo "📦 Starting Redis..."
    redis-server --daemonize yes || redis-server &
    sleep 2
else
    echo "✅ Redis is already running."
fi

source .venv/bin/activate


# Explicitly load .env file properly (handling comments)
if [ -f .env ]; then
    echo "📄 Loading .env file..."
    set -a
    source <(sed 's/#.*//g' .env)
    set +a
fi

# Add current directory to PYTHONPATH explicitly for Celery
export PYTHONPATH=$PWD

echo "👷 Starting Celery Worker..."
celery -A app.workers.celery_app worker --loglevel=info > celery.log 2>&1 &
CELERY_PID=$!
echo "✅ Celery Worker started (PID: $CELERY_PID). Logs in celery.log"

echo "🌐 Starting FastAPI Server at http://localhost:8000"
echo "📜 API Docs available at http://localhost:8000/docs"
echo "⚠️  Press Ctrl+C to stop everything"

# Start Uvicorn in foreground
uvicorn app.main:app --reload --port 8000
