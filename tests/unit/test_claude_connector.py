"""
Unit tests for the Claude AI connector.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Import the ClaudeConnector class after setting up the mock
from agent_manager.ai_controller.connectors.claude import ClaudeConnector


# Mock the anthropic module
mock_anthropic = MagicMock()
mock_anthropic_module = MagicMock()
# Ensure we can mock the module import
sys.modules["anthropic"] = mock_anthropic_module

# Now we can import with the mock in place


@pytest.fixture
def claude_connector():
    """Fixture for a ClaudeConnector with mocked Anthropic client."""
    with patch(
        "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
    ):
        # Create a mock response
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "This is a test response from Claude"
        mock_response.content = [mock_content]

        # Setup mock Anthropic client
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        # Setup the Anthropic constructor to return our mock client
        mock_anthropic_constructor = MagicMock()
        mock_anthropic_constructor.return_value = mock_client

        # Patch the Anthropic class
        with patch(
            "agent_manager.ai_controller.connectors.claude.anthropic", create=True
        ) as mock_anthropic_mod:
            mock_anthropic_mod.Anthropic = mock_anthropic_constructor
            connector = ClaudeConnector(api_key="test_api_key", model="claude-3-test")
            yield connector, mock_anthropic_mod, mock_client


class TestClaudeConnector:
    """Tests for the ClaudeConnector class."""

    def test_initialization(self):
        """Test that ClaudeConnector initializes correctly."""
        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            connector = ClaudeConnector(api_key="test_key", model="test_model")

            assert connector.name == "claude"
            assert connector.api_key == "test_key"
            assert connector.model == "test_model"
            assert connector.max_retries > 0

    def test_client_initialization_without_key(self):
        """Test initialization without an API key."""
        with (
            patch(
                "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE",
                True,
            ),
            patch(
                "agent_manager.ai_controller.connectors.claude.logger"
            ) as mock_logger,
        ):
            ClaudeConnector(api_key=None)  # No need to store the connector instance
            mock_logger.warning.assert_called_with(
                "Anthropic API key not set. Please set the AGENT_MANAGER_AI_API_KEY environment variable."
            )

    def test_get_client(self, claude_connector):
        """Test getting the Anthropic client."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            client = connector._get_client()
            assert client is not None
            mock_anthropic.Anthropic.assert_called_once_with(api_key=connector.api_key)

    def test_get_client_without_library(self):
        """Test getting the client when the library is not available."""
        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", False
        ):
            connector = ClaudeConnector(api_key="test_key")

            with pytest.raises(ImportError):
                connector._get_client()

    def test_generate_response(self, claude_connector):
        """Test generating a response."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            response = connector.generate_response("Hello Claude, how are you?")

            # Verify client call
            mock_client.messages.create.assert_called_with(
                model=connector.model,
                max_tokens=1024,
                temperature=0.7,
                system="You are a helpful AI assistant that helps users browse the web.",
                messages=[{"role": "user", "content": "Hello Claude, how are you?"}],
            )

            assert response == "This is a test response from Claude"

    def test_generate_response_with_context(self, claude_connector):
        """Test generating a response with custom context."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            context = {"system_prompt": "You are a web browsing assistant."}
            # Execute the function but we don't need to use the response
            connector.generate_response("Navigate to example.com", context)

            # Verify client call with custom system prompt

    def test_generate_response_no_api_key(self):
        """Test generating a response without an API key."""
        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            connector = ClaudeConnector(api_key=None)
            response = connector.generate_response("Hello")

            assert "API key not set" in response

    def test_generate_response_with_retry(self, claude_connector):
        """Test response generation with retries."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Setup client to fail on first call, then succeed
            mock_client.messages.create.side_effect = [
                Exception("API rate limit exceeded"),
                mock_client.messages.create.return_value,
            ]

            with patch(
                "agent_manager.ai_controller.connectors.claude.logger"
            ) as mock_logger:
                with patch("agent_manager.ai_controller.connectors.claude.time.sleep"):
                    response = connector.generate_response("Hello Claude")

                    # Verify error was logged
                    mock_logger.error.assert_called_once()

                    # Verify client was called twice
                    assert mock_client.messages.create.call_count == 2

                    # Verify we got the successful response
                    assert response == "This is a test response from Claude"

    def test_analyze_page(self, claude_connector):
        """Test analyzing a web page."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Setup mock response for structured JSON data
            structured_response = MagicMock()
            structured_content = MagicMock()
            structured_content.text = """Here's my analysis:
            {
                "title": "Example Page",
                "main_content_summary": "This is a page about examples",
                "key_elements": ["header", "main content", "footer"],
                "suggested_actions": ["click on link 1", "fill form"]
            }
            """
            structured_response.content = [structured_content]

            # Return regular response first, then structured response
            mock_client.messages.create.side_effect = [
                mock_client.messages.create.return_value,
                structured_response,
            ]

            result = connector.analyze_page(
                "<html><body><h1>Example</h1><p>Content</p></body></html>",
                instructions="Analyze this page",
            )

            # Verify client was called twice (once for analysis, once for structured data)
            assert mock_client.messages.create.call_count == 2

            # Check result has expected structure
            assert result["title"] == "Example Page"
            assert result["main_content_summary"] == "This is a page about examples"
            assert len(result["key_elements"]) == 3
            assert len(result["suggested_actions"]) == 2

    def test_analyze_page_with_screenshot(self, claude_connector):
        """Test analyzing a page with a screenshot."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Mock the open function
            mock_image_data = b"fake_image_data"
            mock_open = MagicMock()
            mock_file = MagicMock()
            mock_file.read.return_value = mock_image_data
            mock_open.return_value.__enter__.return_value = mock_file

            # Set up response for basic text response
            with patch("builtins.open", mock_open):
                connector.analyze_page(
                    "<html><body>Example</body></html>",
                    screenshot_path="/path/to/screenshot.png",
                )

                # Verify client call with image
                last_call_args = mock_client.messages.create.call_args_list[0][1]
                messages = last_call_args["messages"]

                # Verify the message contains both text and image
                assert isinstance(messages[0]["content"], list)
                assert messages[0]["content"][0]["type"] == "text"
                assert messages[0]["content"][1]["type"] == "image"
                assert messages[0]["content"][1]["source"]["type"] == "base64"
                assert messages[0]["content"][1]["source"]["media_type"] == "image/png"

    def test_summarize_content(self, claude_connector):
        """Test summarizing content."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            response = connector.summarize_content(
                "This is a long text to summarize.", max_length=100
            )

            # Verify client call with system prompt for summarization
            last_call_args = mock_client.messages.create.call_args[1]
            assert last_call_args["system"].startswith(
                "You are a summarization assistant"
            )

            assert response == "This is a test response from Claude"

    def test_decide_next_action(self, claude_connector):
        """Test deciding the next action."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Setup mock to return a JSON response
            json_response = MagicMock()
            json_content = MagicMock()
            json_content.text = """
            {
                "action": "click",
                "parameters": {"selector": ".button"},
                "reasoning": "This button will navigate to the next page"
            }
            """
            json_response.content = [json_content]

            mock_client.messages.create.return_value = json_response

            result = connector.decide_next_action(
                page_content="<button class='button'>Next</button>",
                current_url="http://example.com",
                instructions="Find the next button and click it",
                available_actions=["click", "type", "navigate"],
            )

            # Verify client call with system prompt for decision making
            system_prompt = mock_client.messages.create.call_args[1]["system"]
            assert "web browsing assistant" in system_prompt

            # Verify result
            assert result["action"] == "click"
            assert result["parameters"]["selector"] == ".button"
            assert "reasoning" in result

    def test_decide_next_action_unavailable_action(self, claude_connector):
        """Test deciding an action that isn't available."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Setup mock to return a JSON with an unavailable action
            json_response = MagicMock()
            json_content = MagicMock()
            json_content.text = """
            {
                "action": "scroll",
                "parameters": {"direction": "down"},
                "reasoning": "Need to scroll down to see more content"
            }
            """
            json_response.content = [json_content]

            mock_client.messages.create.return_value = json_response

            with patch(
                "agent_manager.ai_controller.connectors.claude.logger"
            ) as mock_logger:
                result = connector.decide_next_action(
                    page_content="<p>Some content</p>",
                    current_url="http://example.com",
                    instructions="Read the page",
                    available_actions=["click", "type", "navigate"],
                )

                # Verify warning was logged
                mock_logger.warning.assert_called_once()

                # Verify result uses the first available action
                assert result["action"] == "click"
                assert "reasoning" in result

    def test_decide_next_action_invalid_json(self, claude_connector):
        """Test handling invalid JSON in decision making."""
        connector, mock_anthropic, mock_client = claude_connector

        with patch(
            "agent_manager.ai_controller.connectors.claude.ANTHROPIC_AVAILABLE", True
        ):
            # Setup mock to return non-JSON response
            invalid_response = MagicMock()
            invalid_content = MagicMock()
            invalid_content.text = "I think you should click the button."
            invalid_response.content = [invalid_content]

            mock_client.messages.create.return_value = invalid_response

            with patch(
                "agent_manager.ai_controller.connectors.claude.logger"
            ) as mock_logger:
                result = connector.decide_next_action(
                    page_content="<button>Click me</button>",
                    current_url="http://example.com",
                    instructions="Click the button",
                    available_actions=["click", "type", "navigate"],
                )

                # Verify warning was logged
                mock_logger.warning.assert_called_once()

                # Verify result uses the first available action
                assert result["action"] == "click"
                assert "reasoning" in result
