# Scrum AI Assistant

A production-ready backend service that automates Scrum meeting outcomes into Jira/Azure Boards tasks.

## Overview

Scrum AI Assistant helps remote teams eliminate manual meeting notes and task creation by:
- Ingesting meeting transcripts (audio or text)
- Using AI to extract structured data (decisions, blockers, action items)
- Automatically creating/updating tasks in Jira or Azure Boards
- Tracking task completion and sending follow-up notifications

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Async Jobs**: Celery + Redis
- **Scheduling**: Celery Beat
- **Integrations**: Jira REST API, Slack webhooks
- **Infrastructure**: Docker + Docker Compose

## Architecture

```
scrum-ai-assistant/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # Database setup
│   │   └── logging.py         # Logging configuration
│   ├── models/                # SQLAlchemy models
│   │   ├── meeting.py
│   │   ├── extracted_item.py
│   │   └── task.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── meeting.py
│   │   ├── extracted_item.py
│   │   ├── task.py
│   │   └── extraction.py
│   ├── api/routes/            # API endpoints
│   │   └── meetings.py
│   ├── services/              # Business logic
│   │   ├── meeting_service.py
│   │   ├── ai_service.py
│   │   └── transcription_service.py
│   ├── repositories/          # Data access layer
│   │   ├── meeting_repository.py
│   │   ├── extracted_item_repository.py
│   │   └── task_repository.py
│   ├── integrations/          # External integrations
│   │   ├── base.py
│   │   ├── jira.py
│   │   ├── azure.py
│   │   ├── factory.py
│   │   └── slack.py
│   └── workers/               # Celery tasks
│       ├── celery_app.py
│       ├── tasks.py
│       └── beat_schedule.py
├── alembic/                   # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

### meetings
Stores meeting information and processing status
```sql
- id (PK)
- title (VARCHAR 255)
- ceremony_type (ENUM: STANDUP, PLANNING, REVIEW, RETRO)
- meeting_date (DATETIME)
- tool_type (ENUM: JIRA, AZURE)
- project_key (VARCHAR 50)
- status (ENUM: CREATED, UPLOADED, TRANSCRIBED, EXTRACTED, TASKS_PUSHED, COMPLETED, FAILED)
- transcript (TEXT)
- summary (TEXT)
- audio_filename (VARCHAR 255)
- created_at, updated_at (DATETIME)
```

### extracted_items
Stores decisions, blockers, and action items
```sql
- id (PK)
- meeting_id (FK -> meetings.id)
- item_type (ENUM: DECISION, BLOCKER, ACTION_ITEM)
- content (TEXT - JSON)
- created_at (DATETIME)
```

### tasks
Tracks created tasks in external systems
```sql
- id (PK)
- meeting_id (FK -> meetings.id)
- tool_type (VARCHAR 20)
- external_key_or_id (VARCHAR 50)
- title (VARCHAR 255)
- status (ENUM: NEW, PUSHED, COMPLETED, INCOMPLETE)
- created_at (DATETIME)
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Jira API token for integration

### 1. Clone and Setup

```bash
cd scrum-ai-assistant
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and set your integrations:

```env
# Jira (for real integration)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-api-token
JIRA_USER_EMAIL=user@example.com

# Slack (optional, for notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache/message broker
- FastAPI API (port 8000)
- Celery worker (background jobs)
- Celery Beat scheduler (daily tasks at 9 AM)

### 4. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 5. Verify

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
# Open http://localhost:8000/docs in browser
```

## API Endpoints

### Create Meeting
```bash
curl -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning",
    "ceremony_type": "PLANNING",
    "meeting_date": "2024-01-10T10:00:00",
    "tool_type": "JIRA",
    "project_key": "OB"
  }'
```

Response:
```json
{
  "id": 1,
  "title": "Sprint Planning",
  "ceremony_type": "PLANNING",
  "status": "CREATED",
  "...": "..."
}
```

### Upload Audio
```bash
curl -X POST http://localhost:8000/api/meetings/1/upload-audio \
  -F "file=@meeting.mp3"
```

### Add Transcript
```bash
curl -X POST http://localhost:8000/api/meetings/1/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Meeting transcript text here..."
  }'
```

### Process Meeting
Triggers async processing (transcription, AI extraction, task creation):
```bash
curl -X POST http://localhost:8000/api/meetings/1/process
```

Response:
```json
{
  "started": true,
  "meeting_id": 1
}
```

### Get Meeting Details
```bash
curl http://localhost:8000/api/meetings/1
```

### Get Extracted Items
```bash
curl http://localhost:8000/api/meetings/1/items
```

Response:
```json
{
  "decisions": [
    "Use React Query for data fetching",
    "Schedule database migration"
  ],
  "blockers": [
    {
      "description": "API endpoint not ready",
      "owner": "John"
    }
  ],
  "action_items": []
}
```

### Get Created Tasks
```bash
curl http://localhost:8000/api/meetings/1/tasks
```

Response:
```json
[
  {
    "id": 1,
    "meeting_id": 1,
    "tool_type": "JIRA",
    "external_key_or_id": "OB-123",
    "title": "Complete payment gateway integration",
    "status": "PUSHED",
    "created_at": "2024-01-10T10:00:00"
  }
]
```

### List Meetings
```bash
curl "http://localhost:8000/api/meetings?skip=0&limit=10"
```

## Demo Workflow

1. **Create a meeting:**
```bash
MEETING_ID=$(curl -s -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "OB"
  }' | jq -r '.id')

echo "Created meeting: $MEETING_ID"
```

2. **Add a transcript:**
```bash
curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Good morning everyone. Sarah, what did you work on yesterday? I finished the login feature. Decision: We will use React Query. John is blocked on the API endpoint. Action item: Tom needs to complete payment integration by Friday."
  }'
```

3. **Process the meeting:**
```bash
curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/process
```

4. **Check results:**
```bash
# Get extracted data
curl http://localhost:8000/api/meetings/$MEETING_ID/items

# Get created tasks
curl http://localhost:8000/api/meetings/$MEETING_ID/tasks
```

## Features

### AI Extraction
Currently uses mock implementation. To integrate with real AI:
1. Update `app/services/ai_service.py`
2. Integrate with OpenAI GPT, LLaMA, or similar LLM
3. Use structured prompts to extract decisions, blockers, action items

### Transcription
Currently uses mock implementation. To integrate with real transcription:
1. Update `app/services/transcription_service.py`
2. Integrate with OpenAI Whisper, AWS Transcribe, Google Speech-to-Text, etc.

### Jira Integration
- Creates issues in specified project
- Adds comments to existing issues (detected via pattern matching: `[A-Z]+-\d+`)
- Retrieves issue status for follow-up tracking
- Supports authentication via API token

### Task Follow-up
Daily job runs at 9 AM:
- Fetches tasks created in last 24 hours
- Gets status from Jira/Azure Boards
- Updates local task status (COMPLETED/INCOMPLETE)
- Sends Slack notification for incomplete tasks
- Logs email notifications (stub)

## Configuration

### Logging
- All logs written to `logs/app.log`
- Rotating file handler (10MB max, 5 backups)
- Console output with detailed formatting
- Configurable log level via `LOG_LEVEL` env var

### Database
- Connection pooling (pool_size=10, max_overflow=20)
- Health checks on connection use
- Automatic migrations via Alembic

### Celery
- Three queues: default, processing, notifications
- Task routing optimizes throughput
- Retries with exponential backoff
- Result expiration: 1 hour

## Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Stop services
docker-compose down

# Remove volumes (careful - deletes data!)
docker-compose down -v

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision -m "description"
```

## Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# In another terminal, start Celery Beat
celery -A app.workers.celery_app beat --loglevel=info
```

### Running Tests (stub)

```bash
# To be added: pytest configuration
# pytest tests/
```

## Production Considerations

1. **Security**
   - Use environment variables for secrets
   - Implement API authentication (JWT, OAuth2)
   - Add rate limiting
   - Validate all inputs

2. **Scaling**
   - Add API load balancer (nginx, HAProxy)
   - Multiple Celery workers
   - Redis Sentinel for HA
   - PostgreSQL replication/backup

3. **Monitoring**
   - Implement health checks
   - Add metrics (Prometheus)
   - Centralized logging (ELK, Datadog)
   - Tracing (Jaeger, DataDog)

4. **Reliability**
   - Add request/response validation
   - Implement circuit breaker for external APIs
   - Graceful degradation on integration failures
   - Better error handling and recovery

## Troubleshooting

### Database connection refused
```bash
# Check if postgres is running
docker-compose logs postgres

# Verify health
docker-compose exec postgres pg_isready -U postgres
```

### Celery tasks not running
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping

# Check queued tasks
docker-compose exec redis redis-cli LLEN celery
```

### No tasks created in Jira
```bash
# Verify Jira credentials in .env
# Check API logs
docker-compose logs api | grep -i jira

# Test Jira connectivity manually in logs
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions, open a GitHub issue or contact the development team.

---

**Happy automating Scrum meetings!** 🚀
