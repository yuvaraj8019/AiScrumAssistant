# Configuration Guide

This document explains the environment variables used to configure the application. These should be set in a `.env` file in the project root.

## Database
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://user:pass@localhost:5432/scrum_db` |
| `TEST_DATABASE_URL` | DB for running tests | `postgresql+psycopg://user:pass@localhost:5432/test_db` |

## Redis & Celery
| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis for caching | `redis://localhost:6379` |
| `CELERY_BROKER_URL` | Redis for task queue | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND_URL` | Redis for task results | `redis://localhost:6379/1` |

## Integration - Jira
**Required for Jira task creation.**

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_BASE_URL` | Your Atlassian domain | `https://your-domain.atlassian.net` |
| `JIRA_USER_EMAIL` | Logged-in user email | `user@example.com` |
| `JIRA_API_TOKEN` | Atlassian API Token | `ATATT3x...` (See [how to generate](https://id.atlassian.com/manage-profile/security/api-tokens)) |

## Integration - Slack (Optional)
| Variable | Description | Example |
|----------|-------------|---------|
| `SLACK_WEBHOOK_URL` | For sending alerts | `https://hooks.slack.com/services/...` |

## Integration - AI (Optional)
If not set, the system uses a **Mock AI Service** that returns sample data.

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | For GPT-4 extraction | `sk-...` |

## Application Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `AUDIO_STORAGE_PATH` | Path to save uploads | `/data/audio` |
