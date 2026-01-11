"""
Celery Beat schedule configuration for periodic tasks.
Uses crontab schedule.
"""
from celery.schedules import crontab

from app.workers.celery_app import celery_app

# Schedule configuration
celery_app.conf.beat_schedule = {
    "check-task-completion-daily": {
        "task": "app.workers.tasks.check_task_completion",
        "schedule": crontab(hour=9, minute=0),  # 9 AM every day
        "options": {"queue": "notifications"},
    },
}
