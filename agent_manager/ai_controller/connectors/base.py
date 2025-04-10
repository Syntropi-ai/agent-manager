"""
Base connector for AI model integration.
Defines the interface that all AI connectors should implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AIConnector(ABC):
    """
    Abstract base class for AI model connectors.

    This class defines the interface that all AI connectors must implement
    to provide a consistent way to interact with different AI models.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the AI connector.

        Args:
            **kwargs: Additional configuration parameters
        """
        self.name = "base"
        self.config = kwargs

    @abstractmethod
    def generate_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response from the AI model.

        Args:
            prompt: The prompt to send to the AI model
            context: Optional context information

        Returns:
            The generated response from the AI model
        """
        pass

    @abstractmethod
    def analyze_page(
        self,
        html_content: str,
        screenshot_path: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a web page and determine the next action.

        Args:
            html_content: HTML content of the page
            screenshot_path: Path to a screenshot of the page
            instructions: Specific instructions for analysis

        Returns:
            Dictionary with analysis results and recommended actions
        """
        pass

    @abstractmethod
    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """
        Summarize content.

        Args:
            content: The content to summarize
            max_length: Maximum length of the summary

        Returns:
            Summarized content
        """
        pass

    @abstractmethod
    def decide_next_action(
        self,
        page_content: str,
        current_url: str,
        instructions: str,
        available_actions: List[str],
    ) -> Dict[str, Any]:
        """
        Decide the next action to take based on the current page content and instructions.

        Args:
            page_content: Content of the current page
            current_url: Current URL
            instructions: User instructions
            available_actions: List of available actions

        Returns:
            Dictionary with the decided action and parameters
        """
        pass
