"""
Azure Boards integration service (stubbed for demo).
In production, implement using Azure DevOps REST API.
"""
from app.core.logging import get_logger
from app.integrations.base import ToolIntegration

logger = get_logger(__name__)


class AzureBoardsIntegrationService(ToolIntegration):
    """Azure Boards integration service (demo stub)."""

    def create_issue(self, summary: str, description: str, project_key: str) -> str:
        """Create a new Azure Boards work item (stubbed)."""
        logger.info(f"[STUB] Creating Azure Boards item in project {project_key}: {summary}")
        # In production: integrate with Azure DevOps REST API
        # For demo, return a mock key
        return f"AZURE-{hash(summary) % 10000}"

    def add_comment(self, issue_key: str, comment: str) -> None:
        """Add a comment to an Azure Boards item (stubbed)."""
        logger.info(f"[STUB] Adding comment to Azure Boards item {issue_key}")
        # In production: implement via Azure DevOps REST API

    def get_issue_status(self, issue_key: str) -> str:
        """Get the status of an Azure Boards item (stubbed)."""
        logger.info(f"[STUB] Fetching status for Azure Boards item {issue_key}")
        # In production: implement via Azure DevOps REST API
        return "Active"
