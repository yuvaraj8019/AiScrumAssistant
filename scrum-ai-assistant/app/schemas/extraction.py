"""
Pydantic schemas for extraction results from AI service.
"""
from pydantic import BaseModel, Field


class BlockerSchema(BaseModel):
    """Blocker item schema."""
    description: str
    owner: str | None = None


class ActionItemSchema(BaseModel):
    """Action item schema."""
    title: str
    assignee: str | None = None
    due_date: str | None = None


class ExtractionResult(BaseModel):
    """Result from AI extraction service."""
    summary: str
    decisions: list[str] = Field(default_factory=list)
    blockers: list[BlockerSchema] = Field(default_factory=list)
    action_items: list[ActionItemSchema] = Field(default_factory=list)
