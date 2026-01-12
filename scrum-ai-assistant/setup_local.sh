#!/bin/bash
set -e

echo "🚀 Setting up Scrum AI Assistant locally..."

# 1. Create .env file
echo "📝 Creating .env file..."
cat > .env << EOL
# Database
DATABASE_URL=postgresql+psycopg://localhost:5432/scrum_db

# Redis
REDIS_URL=redis://localhost:6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND_URL=redis://localhost:6379/1

# FastAPI
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
APP_NAME=Scrum AI Assistant
APP_VERSION=1.0.0
EOL

# 2. Python Environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Database
echo "🗄️ Running database migrations..."
# Check if database exists, creation handled previously by agent but good to have fallback
createdb scrum_db 2>/dev/null || true
alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "To run the application, you need 3 terminal windows/tabs:"
echo "1. Redis:   redis-server"
echo "2. Celery:  source .venv/bin/activate && celery -A app.workers.celery_app worker --loglevel=info"
echo "3. API:     source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
