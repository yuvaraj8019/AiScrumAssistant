# Setup Guide

This guide covers how to set up the Scrum AI Assistant locally for development and testing.

## Prerequisites
*   Python 3.10+
*   Docker & Docker Compose (optional, for containerized run)
*   PostgreSQL (if running locally without Docker)
*   Redis (if running locally without Docker)

## Option A: Local Setup (Recommended for Debugging)

### 1. navigate to Project
```bash
cd scrum-ai-assistant
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` with your credentials (see `CONFIG_GUIDE.md`).

### 4. Start Services
Use the provided helper script to start Redis, Celery, and FastAPI:
```bash
bash start_local.sh
```

### 5. Access
*   **API Docs**: http://localhost:8000/docs
*   **API Root**: http://localhost:8000/

---

## Option B: Docker Setup

### 1. Start Containers
```bash
docker-compose up -d --build
```

### 2. Run Migrations
```bash
docker-compose exec api alembic upgrade head
```

### 3. View Logs
```bash
docker-compose logs -f
```

## Troubleshooting
*   **Port Conflicts**: Ensure ports 8000, 5432, 6379 are free.
*   **Database**: If using local Postgres, ensure user/password matches `.env`.
