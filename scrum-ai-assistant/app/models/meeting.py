"""
Meeting model for storing meeting information.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CeremonyType(str, Enum):
    """Scrum ceremony types."""
    STANDUP = "STANDUP"
    PLANNING = "PLANNING"
    REVIEW = "REVIEW"
    RETRO = "RETRO"


class ToolType(str, Enum):
    """Integration tool types."""
    JIRA = "JIRA"
    AZURE = "AZURE"


class MeetingStatus(str, Enum):
    """Meeting processing status."""
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    TRANSCRIBED = "TRANSCRIBED"
    EXTRACTED = "EXTRACTED"
    TASKS_PUSHED = "TASKS_PUSHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Meeting(Base):
    """Meeting model."""
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    ceremony_type: Mapped[str] = mapped_column(
        SQLEnum(CeremonyType),
        nullable=False
    )
    meeting_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tool_type: Mapped[str] = mapped_column(
        SQLEnum(ToolType),
        nullable=False
    )
    project_key: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(MeetingStatus),
        default=MeetingStatus.CREATED,
        nullable=False
    )
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    extracted_items: Mapped[list["ExtractedItem"]] = relationship(
        "ExtractedItem",
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="meeting",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"
