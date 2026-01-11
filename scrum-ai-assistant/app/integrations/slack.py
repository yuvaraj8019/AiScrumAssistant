"""
Slack integration for sending notifications.
"""
from typing import Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SlackNotificationService:
    """Service for sending notifications to Slack."""

    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    def send_message(self, message: str) -> bool:
        """
        Send a message to Slack via webhook.
        
        Args:
            message: Message text
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured, skipping notification")
            return False

        try:
            payload = {"text": message}
            with httpx.Client(timeout=30) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
            logger.info("Slack notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return False

    def send_follow_up(self, meeting_id: int, incomplete_tasks: list) -> bool:
        """
        Send follow-up notification about incomplete tasks.
        
        Args:
            meeting_id: Meeting ID
            incomplete_tasks: List of incomplete tasks
            
        Returns:
            True if sent successfully
        """
        if not incomplete_tasks:
            return True

        task_list = "\n".join([f"• {task.title}" for task in incomplete_tasks])
        message = (
            f"Follow-up: Meeting {meeting_id} still has incomplete tasks:\n{task_list}\n"
            "Please review and update status."
        )

        return self.send_message(message)
