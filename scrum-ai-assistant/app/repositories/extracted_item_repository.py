"""
Repository for ExtractedItem model - handles extracted items database operations.
"""
import json
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.extracted_item import ExtractedItem, ItemType

logger = get_logger(__name__)


class ExtractedItemRepository:
    """Repository for ExtractedItem model operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        meeting_id: int,
        item_type: str,
        content: dict,
    ) -> ExtractedItem:
        """Create a new extracted item."""
        item = ExtractedItem(
            meeting_id=meeting_id,
            item_type=item_type,
            content=json.dumps(content),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"Created extracted item {item.id} for meeting {meeting_id}")
        return item

    def get_by_id(self, item_id: int) -> Optional[ExtractedItem]:
        """Get extracted item by ID."""
        return (
            self.db.query(ExtractedItem)
            .filter(ExtractedItem.id == item_id)
            .first()
        )

    def get_by_meeting_id(self, meeting_id: int) -> List[ExtractedItem]:
        """Get all extracted items for a meeting."""
        return (
            self.db.query(ExtractedItem)
            .filter(ExtractedItem.meeting_id == meeting_id)
            .all()
        )

    def get_by_meeting_and_type(
        self,
        meeting_id: int,
        item_type: str,
    ) -> List[ExtractedItem]:
        """Get extracted items by meeting ID and type."""
        return (
            self.db.query(ExtractedItem)
            .filter(
                ExtractedItem.meeting_id == meeting_id,
                ExtractedItem.item_type == item_type,
            )
            .all()
        )

    def delete(self, item_id: int) -> bool:
        """Delete an extracted item."""
        item = self.get_by_id(item_id)
        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        logger.info(f"Deleted extracted item {item_id}")
        return True

    def delete_by_meeting_id(self, meeting_id: int) -> int:
        """Delete all extracted items for a meeting."""
        count = (
            self.db.query(ExtractedItem)
            .filter(ExtractedItem.meeting_id == meeting_id)
            .delete()
        )
        self.db.commit()
        logger.info(f"Deleted {count} extracted items for meeting {meeting_id}")
        return count
