"""
Pydantic schemas for tasks.
"""
from datetime import datetime
from pydantic import BaseModel


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    meeting_id: int
    tool_type: str
    external_key_or_id: str
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
