"""
Extracted items model for storing extracted decisions, blockers, and action items.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ItemType(str, Enum):
    """Types of extracted items."""
    DECISION = "DECISION"
    BLOCKER = "BLOCKER"
    ACTION_ITEM = "ACTION_ITEM"


class ExtractedItem(Base):
    """Extracted items from meeting transcripts."""
    __tablename__ = "extracted_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False
    )
    item_type: Mapped[str] = mapped_column(
        SQLEnum(ItemType),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(
        "Meeting",
        back_populates="extracted_items"
    )

    def __repr__(self) -> str:
        return f"<ExtractedItem(id={self.id}, type={self.item_type})>"
