"""
Pydantic schemas for extracted items.
"""
from datetime import datetime
from pydantic import BaseModel


class ExtractedItemResponse(BaseModel):
    """Schema for extracted item response."""
    id: int
    meeting_id: int
    item_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
