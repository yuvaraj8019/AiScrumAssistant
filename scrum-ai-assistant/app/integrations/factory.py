"""
Factory for creating tool integration instances based on tool type.
"""
from app.core.logging import get_logger
from app.integrations.base import ToolIntegration
from app.integrations.jira import JiraIntegrationService
from app.integrations.azure import AzureBoardsIntegrationService

logger = get_logger(__name__)


class ToolIntegrationFactory:
    """Factory for creating tool integration instances."""

    @staticmethod
    def create(tool_type: str) -> ToolIntegration:
        """
        Create an integration service instance based on tool type.
        
        Args:
            tool_type: Type of tool (JIRA, AZURE)
            
        Returns:
            Instance of appropriate integration service
            
        Raises:
            ValueError: If tool_type is not supported
        """
        tool_type_upper = tool_type.upper()
        
        if tool_type_upper == "JIRA":
            logger.info("Creating Jira integration service")
            return JiraIntegrationService()
        elif tool_type_upper == "AZURE":
            logger.info("Creating Azure Boards integration service")
            return AzureBoardsIntegrationService()
        else:
            raise ValueError(f"Unsupported tool type: {tool_type}")
