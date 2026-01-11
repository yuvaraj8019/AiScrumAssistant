"""
Pydantic schemas for API requests and responses related to meetings.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    """Schema for creating a new meeting."""
    title: str = Field(..., min_length=1, max_length=255)
    ceremony_type: str
    meeting_date: datetime
    tool_type: str
    project_key: str = Field(..., min_length=1, max_length=50)


class MeetingResponse(BaseModel):
    """Schema for meeting response."""
    id: int
    title: str
    ceremony_type: str
    meeting_date: datetime
    tool_type: str
    project_key: str
    status: str
    transcript: str | None = None
    summary: str | None = None
    audio_filename: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingProcessResponse(BaseModel):
    """Response for processing a meeting."""
    started: bool
    meeting_id: int
