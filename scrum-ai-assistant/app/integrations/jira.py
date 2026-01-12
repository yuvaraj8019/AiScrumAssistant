"""
Jira REST API integration for creating issues and managing tasks.
"""
import base64
from typing import Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.base import ToolIntegration

logger = get_logger(__name__)
settings = get_settings()


class JiraIntegrationService(ToolIntegration):
    """Jira integration service using REST API."""

    def __init__(self):
        self.base_url = settings.JIRA_BASE_URL
        self.user_email = settings.JIRA_USER_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self._setup_auth()

    def _setup_auth(self) -> None:
        """Setup basic authentication header."""
        credentials = f"{self.user_email}:{self.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = {"Authorization": f"Basic {encoded}"}

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None,
    ) -> Optional[dict]:
        """Make HTTP request to Jira API with retry logic."""
        url = f"{self.base_url}/rest/api/3{endpoint}"
        headers = {
            **self.auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=30) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                elif method == "POST":
                    response = client.post(url, headers=headers, json=json_data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json() if response.content else None

        except httpx.HTTPError as e:
            logger.error(f"Jira API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            raise

    def create_issue(self, summary: str, description: str, project_key: str) -> str:
        """Create a new Jira issue."""
        logger.info(f"Creating Jira issue in project {project_key}")

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {"content": [{"content": [{"text": description, "type": "text"}], "type": "paragraph"}], "type": "doc", "version": 1},
                "issuetype": {"id": "10001"},
            }
        }

        try:
            result = self._make_request("POST", "/issue", json_data=payload)
            issue_key = result.get("key")
            logger.info(f"Created Jira issue: {issue_key}")
            return issue_key
        except Exception as e:
            logger.error(f"Failed to create Jira issue: {str(e)}")
            raise

    def add_comment(self, issue_key: str, comment: str) -> None:
        """Add a comment to a Jira issue."""
        logger.info(f"Adding comment to Jira issue {issue_key}")

        payload = {
            "body": {
                "content": [
                    {
                        "content": [{"text": comment, "type": "text"}],
                        "type": "paragraph",
                    }
                ],
                "type": "doc",
                "version": 1,
            }
        }

        try:
            self._make_request("POST", f"/issue/{issue_key}/comment", json_data=payload)
            logger.info(f"Added comment to {issue_key}")
        except Exception as e:
            logger.error(f"Failed to add comment to {issue_key}: {str(e)}")
            raise

    def get_issue_status(self, issue_key: str) -> str:
        """Get the status of a Jira issue."""
        logger.info(f"Fetching status for Jira issue {issue_key}")

        try:
            result = self._make_request("GET", f"/issue/{issue_key}")
            status = result.get("fields", {}).get("status", {}).get("name", "Unknown")
            logger.info(f"Issue {issue_key} status: {status}")
            return status
        except Exception as e:
            logger.error(f"Failed to get issue status for {issue_key}: {str(e)}")
            raise
