"""
AI service interface and mock implementation for extracting structured data from transcripts.
In production, this would integrate with OpenAI GPT, LLaMA, or other LLMs.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.schemas.extraction import (
    ExtractionResult,
    BlockerSchema,
    ActionItemSchema,
)

logger = get_logger(__name__)


class AiService(ABC):
    """Abstract base class for AI extraction services."""

    @abstractmethod
    def extract(self, transcript: str) -> ExtractionResult:
        """
        Extract structured data from transcript.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            ExtractionResult with summary, decisions, blockers, action items
        """
        pass


class MockAiService(AiService):
    """Mock AI service for demo purposes."""

    def extract(self, transcript: str) -> ExtractionResult:
        """
        Mock extraction - returns demo structured data.
        In production, send transcript to OpenAI GPT, LLaMA, or similar LLM with structured prompts.
        """
        logger.info("Mock extracting structured data from transcript")
        
        # Demo extraction result
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        friday = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        
        result = ExtractionResult(
            summary="Team standup covering login feature completion, dashboard development, "
                   "API integration blocker, and payment gateway implementation timeline.",
            decisions=[
                "Use React Query for data fetching across the application",
                "Schedule database migration during maintenance window",
            ],
            blockers=[
                BlockerSchema(
                    description="API endpoint for user profile not ready - blocking dashboard completion",
                    owner="John",
                ),
                BlockerSchema(
                    description="Database migration pending - requires maintenance window scheduling",
                    owner=None,
                ),
            ],
            action_items=[
                ActionItemSchema(
                    title="Complete payment gateway integration",
                    assignee="Tom",
                    due_date=friday,
                ),
                ActionItemSchema(
                    title="Implement user profile settings page",
                    assignee="Sarah",
                    due_date=friday,
                ),
                ActionItemSchema(
                    title="Investigate API endpoint readiness",
                    assignee="John",
                    due_date=tomorrow,
                ),
            ],
        )
        
        logger.info("Mock extraction completed")
        return result
