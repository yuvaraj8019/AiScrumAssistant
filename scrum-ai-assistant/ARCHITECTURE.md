# Scrum AI Assistant - Architecture & Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENTS / USERS                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  FastAPI Server  │  (Port 8000)
                    │   (API Layer)    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────────┐  ┌────────▼──────┐  ┌────────▼────────┐
   │  PostgreSQL │  │     Redis     │  │  Celery Worker │
   │  Database   │  │  (Message     │  │  (Background   │
   │             │  │   Broker)     │  │   Jobs)        │
   └─────────────┘  └────────┬──────┘  └────────┬────────┘
                             │                   │
                    ┌────────▼──────────────────┘
                    │
            ┌───────▼─────────┐
            │ Celery Beat     │  (Scheduler)
            │ (9 AM Daily)    │
            └─────────────────┘

┌──────────────────────────────────────┐
│     External Integrations            │
├──────────────────────────────────────┤
│ • Jira (REST API)                   │
│ • Azure Boards (REST API)           │
│ • Slack (Webhooks)                  │
│ • AI Service (OpenAI/LLM)           │
│ • Transcription (Whisper/AWS)       │
└──────────────────────────────────────┘
```

## Data Flow

### 1. Meeting Creation & Processing Flow

```
User Request (Create Meeting)
    ↓
API Endpoint: POST /api/meetings
    ↓
Meeting Service: create_meeting()
    ↓
Database: INSERT into meetings (status=CREATED)
    ↓
Response: { id, status, ... }
```

### 2. Audio Upload & Transcription Flow

```
User Request (Upload Audio)
    ↓
API Endpoint: POST /api/meetings/{id}/upload-audio
    ↓
Meeting Service: upload_audio()
    ↓
File System: Save to /data/audio/
Database: UPDATE meetings (audio_filename, status=UPLOADED)
    ↓
User Request (Process Meeting)
    ↓
API Endpoint: POST /api/meetings/{id}/process
    ↓
Celery Task: process_meeting(meeting_id)
    ↓
Queue: Added to Redis (processing queue)
    ↓
Celery Worker: Picks up task
    ↓
Transcription Service: transcribe(audio_path)
    ↓
Database: UPDATE meetings (transcript, status=TRANSCRIBED)
```

### 3. AI Extraction & Task Creation Flow

```
Celery Worker: Continue process_meeting()
    ↓
AI Service: extract(transcript)
    ↓
Parsing: Extract decisions, blockers, action items
    ↓
Database: INSERT into extracted_items
Database: UPDATE meetings (summary, status=EXTRACTED)
    ↓
Task Creation Loop:
  For each action_item:
    ↓
    Check for existing Jira keys in transcript (pattern: [A-Z]+-\d+)
    ↓
    If exists: Integration.add_comment(key, action_item)
    If not:    Integration.create_issue(action_item)
    ↓
    Database: INSERT into tasks
    ↓
Database: UPDATE meetings (status=TASKS_PUSHED)
```

### 4. Daily Follow-up Task Flow

```
Celery Beat Scheduler: 9 AM Every Day
    ↓
Celery Task: check_task_completion()
    ↓
Database: SELECT tasks WHERE created_at >= (now - 24h)
    ↓
For each task:
  ↓
  Integration: get_issue_status(external_key)
  ↓
  Status Mapping:
    Done/Completed/Resolved → COMPLETED
    Other → INCOMPLETE
  ↓
  Database: UPDATE tasks (status)
  ↓
If INCOMPLETE tasks exist:
  ↓
  Slack Service: send_follow_up(incomplete_tasks)
  Email Service: log_notification(incomplete_tasks)
```

## Service Components

### Core Services

#### API Service (FastAPI)
- **Port**: 8000
- **Endpoints**: RESTful API for all operations
- **Features**: Health checks, automatic documentation (Swagger)
- **Concurrency**: Handles multiple concurrent requests
- **Features**: CORS, middleware support

#### Database Service (PostgreSQL)
- **Port**: 5432
- **Features**: Transactions, ACID compliance, indexes
- **Connection Pool**: 10 connections, 20 overflow
- **Health Checks**: Pre-ping before use
- **Migrations**: Alembic version control

#### Message Broker (Redis)
- **Port**: 6379
- **Role**: Celery broker and result backend
- **Queues**: default, processing, notifications
- **Persistence**: Optional (configurable)

#### Worker Service (Celery)
- **Tasks**: Long-running async jobs
- **Retries**: Exponential backoff (3 retries)
- **Timeouts**: Soft limit 25 min, hard limit 30 min
- **Queues**: Processing, notifications

#### Scheduler Service (Celery Beat)
- **Schedule**: 9 AM daily follow-up check
- **Task**: Check task completion, send notifications

## Database Schema

### Meetings Table
```sql
Column              Type          Constraints
─────────────────────────────────────────────
id                  SERIAL        PRIMARY KEY
title               VARCHAR(255)  NOT NULL
ceremony_type       ENUM          STANDUP, PLANNING, REVIEW, RETRO
meeting_date        DATETIME      NOT NULL
tool_type           ENUM          JIRA, AZURE
project_key         VARCHAR(50)   NOT NULL
status              ENUM          CREATED, UPLOADED, TRANSCRIBED, EXTRACTED, TASKS_PUSHED, COMPLETED, FAILED
transcript          TEXT          NULL
summary             TEXT          NULL
audio_filename      VARCHAR(255)  NULL
created_at          DATETIME      NOT NULL (auto)
updated_at          DATETIME      NOT NULL (auto)

Indexes: status, project_key
```

### Extracted Items Table
```sql
Column              Type          Constraints
─────────────────────────────────────────────
id                  SERIAL        PRIMARY KEY
meeting_id          INT           FOREIGN KEY → meetings.id (CASCADE)
item_type           ENUM          DECISION, BLOCKER, ACTION_ITEM
content             TEXT          JSON string
created_at          DATETIME      NOT NULL (auto)

Indexes: meeting_id, item_type
```

### Tasks Table
```sql
Column              Type          Constraints
─────────────────────────────────────────────
id                  SERIAL        PRIMARY KEY
meeting_id          INT           FOREIGN KEY → meetings.id (CASCADE)
tool_type           VARCHAR(20)   JIRA, AZURE
external_key_or_id  VARCHAR(50)   NOT NULL
title               VARCHAR(255)  NOT NULL
status              ENUM          NEW, PUSHED, COMPLETED, INCOMPLETE
created_at          DATETIME      NOT NULL (auto)

Indexes: meeting_id, external_key_or_id, status
```

## Deployment Models

### Development
```bash
# Single machine, all services
docker-compose up -d

# Logs visible, hot-reload, full debugging
```

### Production (Single Server)
```yaml
# Production docker-compose.yml
- PostgreSQL with persistent volume
- Redis with sentinel (optional)
- API: Load balanced with nginx
- Celery: Multiple workers
- Monitoring: Prometheus + Grafana
```

### Production (Kubernetes)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: scrum-ai
spec:
  containers:
  - name: api
    image: scrum-ai:latest
    ports:
    - containerPort: 8000
  - name: worker
    image: scrum-ai:latest
    command: ["celery", "-A", "app.workers.celery_app", "worker"]
  - name: beat
    image: scrum-ai:latest
    command: ["celery", "-A", "app.workers.celery_app", "beat"]
```

## Configuration Management

### Environment Variables

| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| DATABASE_URL | PostgreSQL connection | postgresql://... | No (has default) |
| REDIS_URL | Redis connection | redis://redis:6379 | No |
| CELERY_BROKER_URL | Celery broker | redis://redis:6379/0 | No |
| JIRA_BASE_URL | Jira instance URL | https://your-domain.atlassian.net | Yes (for Jira) |
| JIRA_API_TOKEN | Jira API token | your-token | Yes (for Jira) |
| JIRA_USER_EMAIL | Jira user email | user@example.com | Yes (for Jira) |
| SLACK_WEBHOOK_URL | Slack notification webhook | Optional | No |
| DEBUG | Debug mode | False | No |
| LOG_LEVEL | Logging level | INFO | No |

## Error Handling & Retries

### API Errors
```python
# Request validation errors: 400 Bad Request
# Not found errors: 404 Not Found
# Server errors: 500 Internal Server Error
# All errors include descriptive messages
```

### Task Retries
```python
# Celery task configuration
max_retries = 3
retry_delay = 60 seconds (exponential backoff)
# Formula: 60 * (2 ** retry_count)
# Retry 1: 60s, Retry 2: 120s, Retry 3: 240s
```

### Integration Failures
```python
# Jira API errors are logged
# Slack notification failures are non-blocking
# Processing continues even if notification fails
# Fallback to email logging (stub)
```

## Security Considerations

### Development
- All debug endpoints enabled
- Mock services for testing
- SQLite or PostgreSQL in docker

### Production Checklist

- [ ] Use environment variables for all secrets
- [ ] Implement API authentication (JWT/OAuth2)
- [ ] Add rate limiting (Redis-based)
- [ ] Use HTTPS/TLS for all communications
- [ ] Implement request validation & sanitization
- [ ] Add request logging & monitoring
- [ ] Use secrets management (Vault, AWS Secrets)
- [ ] Regular dependency updates
- [ ] Database backups (daily)
- [ ] Log aggregation (ELK, Datadog)
- [ ] Distributed tracing (Jaeger)
- [ ] Health checks & alerts
- [ ] Zero-downtime deployments

## Performance Optimization

### Database Optimization
```python
# Indexes on frequently queried columns
- meetings.status
- meetings.project_key
- extracted_items.meeting_id
- tasks.meeting_id, external_key_or_id, status

# Connection pooling
pool_size = 10
max_overflow = 20

# Query optimization
- Use SQLAlchemy select() for complex queries
- Lazy loading relationships
- Pagination for list endpoints
```

### Celery Optimization
```python
# Task routing
- Processing tasks → dedicated queue
- Notifications → separate queue
- Default tasks → default queue

# Worker tuning
- Processes = number of CPU cores + 1
- Max tasks per worker = 1000
- Worker timeout = 25 minutes

# Redis tuning
- maxmemory-policy = allkeys-lru
- Persistence: AOF or RDB based on use case
```

### API Optimization
```python
# Response compression
- Enable gzip middleware
- Minimize JSON payload size

# Caching
- Cache meeting details (5 min TTL)
- Cache task list per meeting (1 min TTL)

# Pagination
- Default limit: 100 items
- Maximum limit: 1000 items
```

## Monitoring & Observability

### Logging
```python
# Structured logging
{
  "timestamp": "2024-01-10T10:00:00Z",
  "level": "INFO",
  "service": "api",
  "message": "Processing meeting 123",
  "meeting_id": 123,
  "user": "user@example.com"
}

# Log locations
- Console: Real-time output
- File: logs/app.log (rotating)
- Centralized: ELK, Datadog, CloudWatch
```

### Metrics (Prometheus)
```
# API metrics
- http_requests_total
- http_request_duration_seconds
- http_request_size_bytes
- http_response_size_bytes

# Database metrics
- db_connection_pool_size
- db_query_duration_seconds

# Celery metrics
- celery_tasks_total
- celery_task_duration_seconds
- celery_task_failures_total
```

### Health Checks
```bash
# API health
GET /health → { status: "healthy" }

# Database health
SELECT 1 → Connection successful

# Redis health
PING → PONG

# Celery worker
celery inspect active → Active tasks list
```

## Scaling Strategy

### Horizontal Scaling

#### API Layer
```bash
# Multiple API instances behind load balancer
docker-compose up -d --scale api=3
# Nginx load balancer routes requests
```

#### Celery Workers
```bash
# Multiple worker instances
docker-compose up -d --scale celery_worker=5
# Automatic task distribution via Redis
```

#### Database
```yaml
# PostgreSQL replication
- Primary: Master (write)
- Replicas: Read-only (read)
- Connection pooling: PgBouncer
```

### Vertical Scaling
```bash
# Increase resources per service
# CPU: 1 core → 4 cores
# Memory: 512MB → 4GB
# Storage: Add SSD for database
```

## Disaster Recovery

### Backup Strategy
```bash
# Database backups
docker-compose exec postgres pg_dump -U postgres scrum_db > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U postgres

# Frequency: Daily
# Retention: 30 days
# Location: AWS S3 / Cloud storage
```

### High Availability
```yaml
# PostgreSQL replication
- Replication lag monitoring
- Automatic failover
- Connection pooling for load distribution

# Redis Sentinel
- Redis high availability
- Automatic failover
- Master-slave monitoring
```

## Cost Optimization

### Cloud Deployment (AWS/GCP/Azure)
```
# Estimated costs (monthly)
- API Instance: $20-50 (t3.small)
- Database: $20-100 (RDS)
- Redis: $10-50 (ElastiCache)
- Storage: $5-20 (S3/Cloud Storage)
- Total: ~$100-220/month for small scale
```

### Resource Management
```yaml
# Set appropriate resource limits
api:
  mem_limit: 512m
  cpus: 0.5

worker:
  mem_limit: 1g
  cpus: 1

postgres:
  mem_limit: 2g
  cpus: 2
```

---

**For questions or issues, refer to README.md and QUICKSTART.md**
