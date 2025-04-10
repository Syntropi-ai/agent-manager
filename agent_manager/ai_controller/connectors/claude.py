"""
Claude AI connector for integration with Anthropic's Claude model.
"""

import base64
import json
import time
from typing import Any, Dict, List, Optional

try:
    import anthropic  # type: ignore

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from agent_manager.ai_controller.connectors.base import AIConnector
from agent_manager.utils.config import config
from agent_manager.utils.logger import logger


class ClaudeConnector(AIConnector):
    """
    Connector for Anthropic's Claude AI model.

    This connector implements the AI interface using Anthropic's Claude API.
    It requires an API key to be set in the configuration.
    """

    def __init__(
        self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Initialize the Claude connector.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.name = "claude"
        self.api_key = api_key or config.get("AI_API_KEY")
        self.model = model or config.get("AI_MODEL", "claude-3-opus-20240229")
        self.max_retries = config.get("AI_MAX_RETRIES", 3)

        if not ANTHROPIC_AVAILABLE:
            logger.warning(
                "Anthropic library not available. Please install with 'pip install anthropic'"
            )

        if not self.api_key:
            logger.warning(
                "Anthropic API key not set. Please set the AGENT_MANAGER_AI_API_KEY environment variable."
            )

    def _get_client(self) -> Any:
        """
        Get an Anthropic client instance.

        Returns:
            Anthropic client

        Raises:
            ImportError: If the Anthropic library is not available
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic library not available. Please install with 'pip install anthropic'"
            )

        return anthropic.Anthropic(api_key=self.api_key)

    def generate_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response from the Claude model.

        Args:
            prompt: The prompt to send to Claude
            context: Optional context information

        Returns:
            The generated response from Claude
        """
        if not self.api_key:
            return "API key not set. Please configure your Anthropic API key."

        context = context or {}
        system_prompt = context.get(
            "system_prompt",
            "You are a helpful AI assistant that helps users browse the web.",
        )

        client = self._get_client()

        for attempt in range(self.max_retries):
            try:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Ensure we return a string type for mypy
                response_text: str = response.content[0].text
                return response_text

            except Exception as e:
                logger.error(
                    f"Error generating response (attempt {attempt+1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    return f"Error generating response: {str(e)}"

        # This return statement ensures a return for all code paths
        return "Failed to generate response after all retries"

    def analyze_page(
        self,
        html_content: str,
        screenshot_path: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a web page using Claude and determine the next action.

        Args:
            html_content: HTML content of the page
            screenshot_path: Path to a screenshot of the page
            instructions: Specific instructions for analysis

        Returns:
            Dictionary with analysis results and recommended actions
        """
        # Truncate HTML content if too large
        html_truncated = (
            html_content[:100000] if len(html_content) > 100000 else html_content
        )

        # Build the prompt
        prompt_parts = [
            "Please analyze this web page and help me understand its content and structure.",
            f"Current instructions: {instructions}" if instructions else "",
            "HTML content (may be truncated):",
            html_truncated,
        ]

        # If a screenshot is provided, encode it as base64 and include in the prompt
        image_content = None
        if screenshot_path:
            try:
                with open(screenshot_path, "rb") as image_file:
                    image_content = base64.b64encode(image_file.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Failed to load screenshot: {e}")

        prompt = "\n\n".join([p for p in prompt_parts if p])

        # Create messages with properly typed content
        messages: List[Dict[str, Any]] = [{"role": "user", "content": prompt}]

        # Add image if available
        if image_content:
            messages = [
                {
                    "role": "user",
                    "content": [  # type: ignore
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_content,
                            },
                        },
                    ],
                }
            ]

        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.5,
                system="You are a helpful AI assistant that analyzes web pages and extracts useful information. Provide a structured analysis with main content, key elements, and suggested actions.",
                messages=messages,
            )

            analysis_text = response.content[0].text

            # Try to extract structured data from the response
            try:
                # Add structure markers to help parse the response
                structured_prompt = "Please provide your analysis in JSON format at the end of your response, with the following fields: 'title', 'main_content_summary', 'key_elements', and 'suggested_actions'."

                structured_response = self.generate_response(
                    prompt + "\n\n" + structured_prompt,
                    {
                        "system_prompt": "You analyze web pages and always output a JSON structure with your findings."
                    },
                )

                # Try to extract JSON from the response
                json_start = structured_response.find("{")
                json_end = structured_response.rfind("}") + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = structured_response[json_start:json_end]
                    # Explicit cast to satisfy mypy
                    analysis: Dict[str, Any] = json.loads(json_str)
                else:
                    analysis = {
                        "title": "Unable to parse structured data",
                        "main_content_summary": analysis_text,
                        "key_elements": [],
                        "suggested_actions": [],
                    }
            except Exception as e:
                logger.warning(f"Failed to parse structured analysis: {e}")
                analysis = {
                    "title": "Error parsing structured data",
                    "main_content_summary": analysis_text,
                    "key_elements": [],
                    "suggested_actions": [],
                }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            return {
                "error": str(e),
                "main_content_summary": "Error analyzing the page.",
                "key_elements": [],
                "suggested_actions": [],
            }

    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """
        Summarize content using Claude.

        Args:
            content: The content to summarize
            max_length: Maximum length of the summary

        Returns:
            Summarized content
        """
        # Truncate content if too large
        content_truncated = content[:50000] if len(content) > 50000 else content

        prompt = f"""Please summarize the following content in about {max_length} characters:

{content_truncated}

Your summary should capture the main points and key information."""

        try:
            summary = self.generate_response(
                prompt,
                {
                    "system_prompt": f"You are a summarization assistant. Create concise summaries of no more than {max_length} characters."
                },
            )

            # Ensure the summary is within the length limit
            if len(summary) > max_length:
                summary = summary[: max_length - 3] + "..."

            return summary

        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return f"Error summarizing content: {str(e)}"

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
        # Format available actions as a list
        actions_formatted = "\n".join([f"- {action}" for action in available_actions])

        # Truncate page content if too large
        page_truncated = (
            page_content[:50000] if len(page_content) > 50000 else page_content
        )

        prompt = f"""Current URL: {current_url}

User Instructions: {instructions}

Available Actions:
{actions_formatted}

Page Content (may be truncated):
{page_truncated}

Based on the page content and user instructions, what should I do next? 
Return a JSON object with the following structure:
{{
    "action": "one of the available actions",
    "parameters": {{ "param1": "value1", ... }},
    "reasoning": "Your reasoning for this decision"
}}"""

        try:
            response = self.generate_response(
                prompt,
                {
                    "system_prompt": "You are a web browsing assistant that makes decisions about what actions to take. Always respond with a valid JSON object."
                },
            )

            # Try to extract JSON from the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                # Explicit cast to Dict[str, Any] to satisfy mypy
                decision: Dict[str, Any] = json.loads(json_str)

                # Validate that the action is in the available actions
                if decision.get("action") not in available_actions:
                    logger.warning(
                        f"AI suggested unavailable action: {decision.get('action')}"
                    )
                    decision["action"] = available_actions[
                        0
                    ]  # Default to the first action
                    decision["parameters"] = {}
                    decision["reasoning"] = (
                        "The originally suggested action was not available."
                    )

                return decision
            else:
                logger.warning("Failed to parse JSON from response")
                return {
                    "action": available_actions[0],
                    "parameters": {},
                    "reasoning": "Failed to parse a structured decision. Defaulting to the first available action.",
                }

        except Exception as e:
            logger.error(f"Error deciding next action: {e}")
            return {
                "action": available_actions[0],
                "parameters": {},
                "reasoning": f"Error: {str(e)}",
            }
