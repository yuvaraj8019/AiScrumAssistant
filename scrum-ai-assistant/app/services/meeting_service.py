"""
Meeting service - orchestrates meeting processing and task management.
"""
import json
import os
import re
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.meeting import Meeting, MeetingStatus
from app.models.extracted_item import ItemType
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.extracted_item_repository import ExtractedItemRepository
from app.repositories.task_repository import TaskRepository
from app.services.transcription_service import MockTranscriptionService
from app.services.ai_service import MockAiService
from app.integrations.factory import ToolIntegrationFactory

logger = get_logger(__name__)
settings = get_settings()


class MeetingService:
    """Service for managing meeting operations."""

    def __init__(self, db: Session):
        self.db = db
        self.meeting_repo = MeetingRepository(db)
        self.item_repo = ExtractedItemRepository(db)
        self.task_repo = TaskRepository(db)
        self.transcription_service = MockTranscriptionService()
        self.ai_service = MockAiService()

    def create_meeting(
        self,
        title: str,
        ceremony_type: str,
        meeting_date,
        tool_type: str,
        project_key: str,
    ) -> Meeting:
        """Create a new meeting."""
        return self.meeting_repo.create(
            title=title,
            ceremony_type=ceremony_type,
            meeting_date=meeting_date,
            tool_type=tool_type,
            project_key=project_key,
        )

    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID."""
        return self.meeting_repo.get_by_id(meeting_id)

    def upload_audio(self, meeting_id: int, file_content: bytes, filename: str) -> bool:
        """Save uploaded audio file."""
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            logger.error(f"Meeting {meeting_id} not found")
            return False

        # Create audio directory if it doesn't exist
        os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)

        # Save file
        file_path = os.path.join(settings.AUDIO_STORAGE_PATH, f"{meeting_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Update meeting
        self.meeting_repo.update(
            meeting_id,
            audio_filename=f"{meeting_id}_{filename}",
            status=MeetingStatus.UPLOADED.value,
        )

        logger.info(f"Saved audio file for meeting {meeting_id}: {file_path}")
        return True

    def add_transcript(self, meeting_id: int, transcript: str) -> Optional[Meeting]:
        """Add or update transcript for a meeting."""
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            logger.error(f"Meeting {meeting_id} not found")
            return None

        return self.meeting_repo.update(
            meeting_id,
            transcript=transcript,
            status=MeetingStatus.UPLOADED.value,
        )

    def process_meeting(self, meeting_id: int) -> bool:
        """
        Process meeting: transcribe (if needed), extract data, create tasks.
        This should be called as a Celery task asynchronously.
        """
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            logger.error(f"Meeting {meeting_id} not found")
            return False

        try:
            # Step 1: Transcribe if audio exists and transcript missing
            if not meeting.transcript and meeting.audio_filename:
                logger.info(f"Transcribing audio for meeting {meeting_id}")
                audio_path = os.path.join(settings.AUDIO_STORAGE_PATH, meeting.audio_filename)
                transcript = self.transcription_service.transcribe(audio_path)
                self.meeting_repo.update(
                    meeting_id,
                    transcript=transcript,
                    status=MeetingStatus.TRANSCRIBED.value,
                )
                meeting = self.meeting_repo.get_by_id(meeting_id)

            # Step 2: Extract structured data
            if not meeting.transcript:
                logger.error(f"No transcript for meeting {meeting_id}")
                self.meeting_repo.update(meeting_id, status=MeetingStatus.FAILED.value)
                return False

            logger.info(f"Extracting data for meeting {meeting_id}")
            extraction_result = self.ai_service.extract(meeting.transcript)

            # Save extraction results to database
            self.meeting_repo.update(
                meeting_id,
                summary=extraction_result.summary,
                status=MeetingStatus.EXTRACTED.value,
            )

            # Save decisions
            for decision in extraction_result.decisions:
                self.item_repo.create(
                    meeting_id=meeting_id,
                    item_type=ItemType.DECISION.value,
                    content={"decision": decision},
                )

            # Save blockers
            for blocker in extraction_result.blockers:
                self.item_repo.create(
                    meeting_id=meeting_id,
                    item_type=ItemType.BLOCKER.value,
                    content={
                        "description": blocker.description,
                        "owner": blocker.owner,
                    },
                )

            # Step 3: Create/update tasks in external system
            logger.info(f"Creating tasks for meeting {meeting_id}")
            self._create_tasks_from_extraction(meeting, extraction_result)

            # Mark meeting as completed
            self.meeting_repo.update(
                meeting_id,
                status=MeetingStatus.TASKS_PUSHED.value,
            )

            logger.info(f"Successfully processed meeting {meeting_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing meeting {meeting_id}: {str(e)}", exc_info=True)
            self.meeting_repo.update(meeting_id, status=MeetingStatus.FAILED.value)
            return False

    def _create_tasks_from_extraction(self, meeting: Meeting, extraction_result) -> None:
        """Create tasks from extraction result in external system."""
        integration = ToolIntegrationFactory.create(meeting.tool_type)

        # Check for existing Jira keys in transcript (pattern: [A-Z]+-\d+)
        existing_keys = re.findall(r"([A-Z]+-\d+)", meeting.transcript or "")

        for action_item in extraction_result.action_items:
            # If an existing key found, add comment to that issue instead of creating new
            if existing_keys:
                for key in existing_keys:
                    comment = (
                        f"Action Item: {action_item.title}\n"
                        f"Assignee: {action_item.assignee or 'Unassigned'}\n"
                        f"Due Date: {action_item.due_date or 'No due date'}"
                    )
                    try:
                        integration.add_comment(key, comment)
                        self.task_repo.create(
                            meeting_id=meeting.id,
                            tool_type=meeting.tool_type,
                            external_key_or_id=key,
                            title=action_item.title,
                        )
                        logger.info(f"Added comment to {key} for meeting {meeting.id}")
                    except Exception as e:
                        logger.error(f"Error adding comment to {key}: {str(e)}")
            else:
                # Create new task
                try:
                    issue_key = integration.create_issue(
                        summary=action_item.title,
                        description=f"Action item from meeting: {meeting.title}\n"
                                   f"Assignee: {action_item.assignee or 'Unassigned'}\n"
                                   f"Due Date: {action_item.due_date or 'No due date'}",
                        project_key=meeting.project_key,
                    )
                    self.task_repo.create(
                        meeting_id=meeting.id,
                        tool_type=meeting.tool_type,
                        external_key_or_id=issue_key,
                        title=action_item.title,
                    )
                    logger.info(f"Created task {issue_key} for meeting {meeting.id}")
                except Exception as e:
                    logger.error(f"Error creating task for meeting {meeting.id}: {str(e)}")

    def get_extracted_items(self, meeting_id: int):
        """Get all extracted items for a meeting."""
        items = self.item_repo.get_by_meeting_id(meeting_id)
        result = {
            "decisions": [],
            "blockers": [],
            "action_items": [],
        }

        for item in items:
            content = json.loads(item.content)
            if item.item_type == ItemType.DECISION.value:
                result["decisions"].append(content.get("decision"))
            elif item.item_type == ItemType.BLOCKER.value:
                result["blockers"].append(content)

        return result

    def get_tasks(self, meeting_id: int):
        """Get all tasks for a meeting."""
        return self.task_repo.get_by_meeting_id(meeting_id)
