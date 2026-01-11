"""
Base integration interface for ticket management systems.
"""
from abc import ABC, abstractmethod


class ToolIntegration(ABC):
    """Abstract base class for tool integrations (Jira, Azure Boards, etc)."""

    @abstractmethod
    def create_issue(self, summary: str, description: str, project_key: str) -> str:
        """
        Create a new issue in the system.
        
        Args:
            summary: Issue title/summary
            description: Issue description
            project_key: Project key/identifier
            
        Returns:
            Issue key or ID (e.g., "OB-123")
        """
        pass

    @abstractmethod
    def add_comment(self, issue_key: str, comment: str) -> None:
        """
        Add a comment to an existing issue.
        
        Args:
            issue_key: Issue key (e.g., "OB-123")
            comment: Comment text
        """
        pass

    @abstractmethod
    def get_issue_status(self, issue_key: str) -> str:
        """
        Get the status of an issue.
        
        Args:
            issue_key: Issue key (e.g., "OB-123")
            
        Returns:
            Status string (e.g., "TO DO", "IN PROGRESS", "DONE")
        """
        pass
