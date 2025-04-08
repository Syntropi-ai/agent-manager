"""
Unit tests for the AI controller component.
"""

import pytest
from unittest.mock import patch, MagicMock
import time

from agent_manager.ai_controller.controller import AIController, AIControllerManager


@pytest.fixture
def ai_controller():
    """Fixture for an AIController instance."""
    controller = AIController("test-session-1", "http://localhost:6901")
    # Mock the connection to avoid actual browser interactions
    controller._connect_to_browser = MagicMock()
    controller._disconnect_from_browser = MagicMock()
    return controller


@pytest.fixture
def ai_controller_manager():
    """Fixture for an AIControllerManager instance."""
    return AIControllerManager()


class TestAIController:
    """Tests for the AIController class."""

    def test_initialize_controller(self):
        """Test that an AIController initializes with correct values."""
        controller = AIController("test-session", "http://test-url")

        assert controller.session_id == "test-session"
        assert controller.browser_url == "http://test-url"
        assert not controller.running
        assert not controller.paused
        assert controller.current_instructions == "Browse the web and summarize content"
        assert controller.control_thread is None

    def test_start_stop_controller(self, ai_controller):
        """Test starting and stopping the controller."""
        # Start the controller
        assert ai_controller.start()
        assert ai_controller.running
        assert not ai_controller.paused
        assert ai_controller.control_thread is not None
        assert ai_controller.control_thread.is_alive()

        # Verify connect was called
        ai_controller._connect_to_browser.assert_called_once()

        # Stop the controller
        assert ai_controller.stop()
        assert not ai_controller.running

        # Give the thread time to finish
        time.sleep(0.1)

        # Verify disconnect was called
        ai_controller._disconnect_from_browser.assert_called_once()

    def test_pause_resume_controller(self, ai_controller):
        """Test pausing and resuming the controller."""
        # Start the controller
        ai_controller.start()

        # Pause the controller
        assert ai_controller.pause()
        assert ai_controller.paused

        # Resume the controller
        assert ai_controller.resume()
        assert not ai_controller.paused

        # Clean up
        ai_controller.stop()

    def test_update_instructions(self, ai_controller):
        """Test updating the controller instructions."""
        new_instructions = "Navigate to example.com and click on the first link"

        # Update instructions
        assert ai_controller.update_instructions(new_instructions)
        assert ai_controller.current_instructions == new_instructions

    def test_get_status(self, ai_controller):
        """Test getting the controller status."""
        # Start the controller
        ai_controller.start()

        # Get status
        status = ai_controller.get_status()

        # Verify status fields
        assert status["session_id"] == "test-session-1"
        assert status["running"] is True
        assert status["paused"] is False
        assert status["current_instructions"] == "Browse the web and summarize content"
        assert "last_action_time" in status

        # Clean up
        ai_controller.stop()

    @patch("threading.Thread")
    def test_control_loop_called(self, mock_thread, ai_controller):
        """Test that the control loop is called when starting."""
        # Use the mock to verify thread creation
        ai_controller.start()

        # Verify Thread was called with the control_loop method
        mock_thread.assert_called_with(target=ai_controller._control_loop)

        # Clean up
        ai_controller.stop()


class TestAIControllerManager:
    """Tests for the AIControllerManager class."""

    def test_create_controller(self, ai_controller_manager):
        """Test creating a controller via the manager."""
        # Patch the AIController class
        with patch(
            "agent_manager.ai_controller.controller.AIController"
        ) as MockAIController:
            # Setup the mock to return a mock controller instance
            mock_controller = MagicMock()
            mock_controller.start.return_value = True
            MockAIController.return_value = mock_controller

            # Create a controller
            controller = ai_controller_manager.create_controller(
                "test-session", "http://test-url"
            )

            # Verify AIController was created with correct args
            MockAIController.assert_called_with("test-session", "http://test-url")

            # Verify start was called
            mock_controller.start.assert_called_once()

            # Verify controller was stored in the manager
            assert ai_controller_manager.controllers["test-session"] == mock_controller

            # Verify the returned controller is our mock
            assert controller == mock_controller

    def test_get_controller(self, ai_controller_manager):
        """Test getting a controller via the manager."""
        # Add a mock controller to the manager
        mock_controller = MagicMock()
        ai_controller_manager.controllers["test-session"] = mock_controller

        # Get the controller
        controller = ai_controller_manager.get_controller("test-session")

        # Verify we got the mock controller
        assert controller == mock_controller

        # Test getting a non-existent controller
        assert ai_controller_manager.get_controller("non-existent") is None

    def test_remove_controller(self, ai_controller_manager):
        """Test removing a controller via the manager."""
        # Add a mock controller to the manager
        mock_controller = MagicMock()
        mock_controller.stop.return_value = True
        ai_controller_manager.controllers["test-session"] = mock_controller

        # Remove the controller
        assert ai_controller_manager.remove_controller("test-session")

        # Verify stop was called
        mock_controller.stop.assert_called_once()

        # Verify the controller was removed from the manager
        assert "test-session" not in ai_controller_manager.controllers

        # Test removing a non-existent controller
        assert not ai_controller_manager.remove_controller("non-existent")

    def test_pause_resume_controller(self, ai_controller_manager):
        """Test pausing and resuming a controller via the manager."""
        # Add a mock controller to the manager
        mock_controller = MagicMock()
        mock_controller.pause.return_value = True
        mock_controller.resume.return_value = True
        ai_controller_manager.controllers["test-session"] = mock_controller

        # Pause the controller
        assert ai_controller_manager.pause_controller("test-session")
        mock_controller.pause.assert_called_once()

        # Resume the controller
        assert ai_controller_manager.resume_controller("test-session")
        mock_controller.resume.assert_called_once()

        # Test with non-existent controller
        assert not ai_controller_manager.pause_controller("non-existent")
        assert not ai_controller_manager.resume_controller("non-existent")

    def test_update_instructions(self, ai_controller_manager):
        """Test updating instructions via the manager."""
        # Add a mock controller to the manager
        mock_controller = MagicMock()
        mock_controller.update_instructions.return_value = True
        ai_controller_manager.controllers["test-session"] = mock_controller

        # Update instructions
        assert ai_controller_manager.update_instructions(
            "test-session", "new instructions"
        )
        mock_controller.update_instructions.assert_called_with("new instructions")

        # Test with non-existent controller
        assert not ai_controller_manager.update_instructions(
            "non-existent", "new instructions"
        )
