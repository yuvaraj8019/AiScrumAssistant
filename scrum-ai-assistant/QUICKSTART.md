# Scrum AI Assistant - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Copy to your workspace
```bash
# The project is already created at:
# /workspaces/AiScrumAssistant/scrum-ai-assistant
cd /workspaces/AiScrumAssistant/scrum-ai-assistant
```

### Step 2: Setup environment
```bash
cp .env.example .env
# Edit .env with your settings (optional for demo)
# - Jira credentials (if using real Jira)
# - Slack webhook URL (if using notifications)
```

### Step 3: Start all services
```bash
docker-compose up -d
```

This starts 5 services:
- **postgres**: Database (port 5432)
- **redis**: Message broker (port 6379)
- **api**: FastAPI server (port 8000)
- **celery_worker**: Async job processor
- **celery_beat**: Daily scheduler (9 AM)

### Step 4: Run database migrations
```bash
docker-compose exec api alembic upgrade head
```

### Step 5: Test the API
```bash
# Health check
curl http://localhost:8000/health

# API docs (open in browser)
# http://localhost:8000/docs
```

## 📝 Complete Example Workflow

```bash
# 1. Create a meeting
RESPONSE=$(curl -s -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning Meeting",
    "ceremony_type": "PLANNING",
    "meeting_date": "2024-01-10T10:00:00",
    "tool_type": "JIRA",
    "project_key": "OB"
  }')

MEETING_ID=$(echo $RESPONSE | jq -r '.id')
echo "Meeting ID: $MEETING_ID"

# 2. Add meeting transcript
curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Good morning team. Let'\''s discuss our sprint goals. We need to complete the OB-123 feature. Sarah will handle the UI, John will do the backend. Decision: Use React Query for API calls. Blocker: Database schema not finalized yet. Action item: Complete payment integration by Friday."
  }'

# 3. Trigger processing (AI extraction + task creation)
curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/process

# Wait a few seconds for processing...
sleep 3

# 4. View extracted items (decisions, blockers)
curl http://localhost:8000/api/meetings/$MEETING_ID/items | jq .

# 5. View created tasks
curl http://localhost:8000/api/meetings/$MEETING_ID/tasks | jq .

# 6. View full meeting details
curl http://localhost:8000/api/meetings/$MEETING_ID | jq .
```

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAREFUL - deletes data!)
docker-compose down -v
```

## 📊 Monitoring

```bash
# View API logs
docker-compose logs -f api

# View Celery worker logs
docker-compose logs -f celery_worker

# View database logs
docker-compose logs -f postgres

# View all logs
docker-compose logs -f
```

## 🔧 Development Commands

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision -m "description"

# Access database shell
docker-compose exec postgres psql -U postgres -d scrum_db

# Access Redis CLI
docker-compose exec redis redis-cli

# Check Celery tasks
docker-compose exec redis redis-cli LLEN celery

# Restart specific service
docker-compose restart api
```

## 🎯 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/meetings` | Create meeting |
| GET | `/api/meetings/{id}` | Get meeting details |
| POST | `/api/meetings/{id}/upload-audio` | Upload audio file |
| POST | `/api/meetings/{id}/transcript` | Add transcript text |
| POST | `/api/meetings/{id}/process` | Start processing (async) |
| GET | `/api/meetings/{id}/items` | Get extracted items |
| GET | `/api/meetings/{id}/tasks` | Get created tasks |
| GET | `/api/meetings` | List all meetings |

## 🧪 Testing with cURL

### Create Meeting
```bash
curl -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "TEST"
  }'
```

### Add Transcript
```bash
curl -X POST http://localhost:8000/api/meetings/1/transcript \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Team meeting discussing OB-123 task"}'
```

### Process Meeting
```bash
curl -X POST http://localhost:8000/api/meetings/1/process
```

### Get Extracted Items
```bash
curl http://localhost:8000/api/meetings/1/items
```

### Get Tasks
```bash
curl http://localhost:8000/api/meetings/1/tasks
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# View error logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Database errors
```bash
# Check if postgres is ready
docker-compose exec postgres pg_isready -U postgres

# Reset database (WARNING: loses data!)
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Celery tasks not running
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check worker logs
docker-compose logs celery_worker

# Check if tasks are queued
docker-compose exec redis redis-cli KEYS "*"
```

## 📚 Project Structure

```
scrum-ai-assistant/
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── core/                 # Configuration & database
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── api/routes/           # REST API endpoints
│   ├── services/             # Business logic
│   ├── repositories/         # Data access layer
│   ├── integrations/         # Jira, Azure, Slack APIs
│   └── workers/              # Celery tasks
├── alembic/                  # Database migrations
├── docker-compose.yml        # Service orchestration
├── requirements.txt          # Python dependencies
└── README.md                 # Full documentation
```

## 🔑 Key Features

✅ **FastAPI REST API** - Modern, fast Python web framework
✅ **PostgreSQL** - Reliable relational database
✅ **SQLAlchemy ORM** - Type-safe database access
✅ **Celery + Redis** - Async job processing
✅ **Jira Integration** - Real REST API integration
✅ **AI Extraction** - Mockable for easy testing
✅ **Slack Notifications** - Follow-up alerts
✅ **Database Migrations** - Alembic for schema management
✅ **Structured Logging** - Production-ready logging
✅ **Docker** - Single-command deployment

## 🎓 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Try the demo workflow** above
3. **Configure Jira integration** with real credentials
4. **Add Slack webhooks** for notifications
5. **Implement real AI/transcription** services
6. **Deploy to production** with proper security

## 💡 Tips

- Use `docker-compose logs -f` to tail logs while testing
- API documentation at `http://localhost:8000/docs` (Swagger UI)
- Database viewer: Use `psql` or DBeaver
- Redis monitor: Use `docker-compose exec redis redis-cli MONITOR`

---

**Ready to automate your Scrum meetings? Let's go! 🚀**
