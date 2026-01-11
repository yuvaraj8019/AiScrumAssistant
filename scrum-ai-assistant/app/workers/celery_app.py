"""
Celery application configuration and setup.
"""
from celery import Celery
from kombu import Exchange, Queue

from app.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery("scrum_ai_assistant")

# Configuration
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    result_expires=3600,
)

# Define queues and exchanges
default_exchange = Exchange("tasks", type="direct")

celery_app.conf.task_queues = (
    Queue(
        "default",
        exchange=default_exchange,
        routing_key="default",
        durable=True,
    ),
    Queue(
        "processing",
        exchange=default_exchange,
        routing_key="processing",
        durable=True,
    ),
    Queue(
        "notifications",
        exchange=default_exchange,
        routing_key="notifications",
        durable=True,
    ),
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange_type = "direct"
celery_app.conf.task_default_routing_key = "default"

# Task routes
celery_app.conf.task_routes = {
    "app.workers.tasks.process_meeting": {"queue": "processing"},
    "app.workers.tasks.check_task_completion": {"queue": "notifications"},
}
