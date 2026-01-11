"""
Task model for storing created tasks in external systems.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TaskStatus(str, Enum):
    """Task status in external systems."""
    NEW = "NEW"
    PUSHED = "PUSHED"
    COMPLETED = "COMPLETED"
    INCOMPLETE = "INCOMPLETE"


class Task(Base):
    """Tasks created in external systems (Jira/Azure)."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False
    )
    tool_type: Mapped[str] = mapped_column(String(20), nullable=False)
    external_key_or_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.NEW,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(
        "Meeting",
        back_populates="tasks"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, external_key={self.external_key_or_id})>"
