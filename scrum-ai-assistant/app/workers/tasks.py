"""
Celery tasks for async processing.
"""
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.workers.celery_app import celery_app
from app.services.meeting_service import MeetingService
from app.repositories.task_repository import TaskRepository
from app.integrations.factory import ToolIntegrationFactory
from app.integrations.slack import SlackNotificationService
from app.models.task import TaskStatus

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_meeting(self, meeting_id: int) -> dict:
    """
    Async task to process meeting: transcribe, extract, and create tasks.
    
    Args:
        meeting_id: ID of meeting to process
        
    Returns:
        Dictionary with processing result
    """
    logger.info(f"Starting to process meeting {meeting_id}")
    db = SessionLocal()
    try:
        service = MeetingService(db)
        success = service.process_meeting(meeting_id)
        return {
            "meeting_id": meeting_id,
            "success": success,
            "status": "completed" if success else "failed",
        }
    except Exception as exc:
        logger.error(f"Error processing meeting {meeting_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def check_task_completion(self) -> dict:
    """
    Daily task to check completion status of recently created tasks.
    Called by Celery Beat scheduler at 9 AM.
    
    Returns:
        Dictionary with summary of checked tasks
    """
    logger.info("Starting daily task completion check")
    db = SessionLocal()
    try:
        task_repo = TaskRepository(db)
        slack_service = SlackNotificationService()

        # Get tasks created in last 24 hours
        recent_tasks = task_repo.get_recent_tasks(hours=24)
        logger.info(f"Found {len(recent_tasks)} recent tasks to check")

        checked_count = 0
        incomplete_tasks = []

        for task in recent_tasks:
            try:
                # Get integration for this task's tool type
                integration = ToolIntegrationFactory.create(task.tool_type)

                # Get current status from external system
                external_status = integration.get_issue_status(task.external_key_or_id)

                # Map external status to our status
                # Assuming "Done", "Completed", or similar means completed
                is_completed = external_status.lower() in [
                    "done",
                    "completed",
                    "resolved",
                    "closed",
                ]

                new_status = (
                    TaskStatus.COMPLETED.value
                    if is_completed
                    else TaskStatus.INCOMPLETE.value
                )

                # Update task status in database
                task_repo.update_status(task.id, new_status)
                checked_count += 1

                if not is_completed:
                    incomplete_tasks.append(task)

                logger.info(
                    f"Updated task {task.external_key_or_id} status to {new_status}"
                )

            except Exception as e:
                logger.error(
                    f"Error checking task {task.external_key_or_id}: {str(e)}"
                )

        # Send follow-up notification if there are incomplete tasks
        if incomplete_tasks:
            logger.info(f"Found {len(incomplete_tasks)} incomplete tasks, sending notification")
            slack_service.send_follow_up(
                meeting_id=incomplete_tasks[0].meeting_id,
                incomplete_tasks=incomplete_tasks,
            )
            # Also log for email (stub)
            logger.info(f"[EMAIL STUB] Incomplete tasks: {[t.title for t in incomplete_tasks]}")

        return {
            "checked_tasks": checked_count,
            "incomplete_count": len(incomplete_tasks),
            "status": "completed",
        }

    except Exception as exc:
        logger.error(f"Error in check_task_completion: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes
    finally:
        db.close()
