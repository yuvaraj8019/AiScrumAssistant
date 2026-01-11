"""
Repository for Meeting model - handles all database operations.
"""
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.meeting import Meeting, MeetingStatus, CeremonyType, ToolType

logger = get_logger(__name__)


class MeetingRepository:
    """Repository for Meeting model operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        title: str,
        ceremony_type: str,
        meeting_date: datetime,
        tool_type: str,
        project_key: str,
    ) -> Meeting:
        """Create a new meeting."""
        meeting = Meeting(
            title=title,
            ceremony_type=ceremony_type,
            meeting_date=meeting_date,
            tool_type=tool_type,
            project_key=project_key,
            status=MeetingStatus.CREATED.value,
        )
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        logger.info(f"Created meeting {meeting.id}: {title}")
        return meeting

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID."""
        return self.db.query(Meeting).filter(Meeting.id == meeting_id).first()

    def update(self, meeting_id: int, **kwargs) -> Optional[Meeting]:
        """Update meeting fields."""
        meeting = self.get_by_id(meeting_id)
        if not meeting:
            return None

        for key, value in kwargs.items():
            if hasattr(meeting, key):
                setattr(meeting, key, value)

        self.db.commit()
        self.db.refresh(meeting)
        logger.info(f"Updated meeting {meeting_id}")
        return meeting

    def get_by_status(self, status: str) -> List[Meeting]:
        """Get meetings by status."""
        return self.db.query(Meeting).filter(Meeting.status == status).all()

    def get_recent_tasks(self, hours: int = 24) -> List[Meeting]:
        """Get meetings with tasks created in last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(Meeting)
            .filter(Meeting.tasks.any())
            .filter(Meeting.updated_at >= cutoff_time)
            .all()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Meeting]:
        """List all meetings with pagination."""
        return self.db.query(Meeting).offset(skip).limit(limit).all()

    def delete(self, meeting_id: int) -> bool:
        """Delete a meeting."""
        meeting = self.get_by_id(meeting_id)
        if not meeting:
            return False

        self.db.delete(meeting)
        self.db.commit()
        logger.info(f"Deleted meeting {meeting_id}")
        return True
