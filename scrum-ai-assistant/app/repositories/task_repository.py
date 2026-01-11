"""
Repository for Task model - handles task database operations.
"""
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.task import Task, TaskStatus

logger = get_logger(__name__)


class TaskRepository:
    """Repository for Task model operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        meeting_id: int,
        tool_type: str,
        external_key_or_id: str,
        title: str,
        status: str = TaskStatus.NEW.value,
    ) -> Task:
        """Create a new task."""
        task = Task(
            meeting_id=meeting_id,
            tool_type=tool_type,
            external_key_or_id=external_key_or_id,
            title=title,
            status=status,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        logger.info(
            f"Created task {task.id}: {external_key_or_id} for meeting {meeting_id}"
        )
        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_external_key(self, external_key: str) -> Optional[Task]:
        """Get task by external key."""
        return (
            self.db.query(Task)
            .filter(Task.external_key_or_id == external_key)
            .first()
        )

    def get_by_meeting_id(self, meeting_id: int) -> List[Task]:
        """Get all tasks for a meeting."""
        return (
            self.db.query(Task)
            .filter(Task.meeting_id == meeting_id)
            .all()
        )

    def get_by_status(self, status: str) -> List[Task]:
        """Get tasks by status."""
        return self.db.query(Task).filter(Task.status == status).all()

    def get_recent_tasks(self, hours: int = 24) -> List[Task]:
        """Get tasks created in last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(Task)
            .filter(Task.created_at >= cutoff_time)
            .all()
        )

    def update_status(self, task_id: int, status: str) -> Optional[Task]:
        """Update task status."""
        task = self.get_by_id(task_id)
        if not task:
            return None

        task.status = status
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"Updated task {task_id} status to {status}")
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task."""
        task = self.get_by_id(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        logger.info(f"Deleted task {task_id}")
        return True
