"""
Unit tests for the Container Manager component.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, ANY

from agent_manager.session_manager.container_manager import ContainerManager


@pytest.fixture
def mock_docker_client():
    """Fixture for a mocked Docker client."""
    with patch("docker.from_env") as mock_client:
        # Create mock networks
        mock_networks = MagicMock()
        mock_networks.list.return_value = []
        mock_networks.create.return_value = MagicMock()

        # Create mock containers
        mock_container = MagicMock()
        mock_container.id = "container123"
        mock_container.status = "running"

        mock_containers = MagicMock()
        mock_containers.run.return_value = mock_container
        mock_containers.get.return_value = mock_container

        # Assign to mock client
        mock_client.return_value.networks = mock_networks
        mock_client.return_value.containers = mock_containers

        yield mock_client.return_value


@pytest.fixture
def container_manager(mock_docker_client):
    """Fixture for a ContainerManager with mocked Docker client."""
    manager = ContainerManager()
    manager.docker_client = mock_docker_client
    return manager


class TestContainerManager:
    """Tests for the ContainerManager class."""

    def test_initialization(self, mock_docker_client):
        """Test that ContainerManager initializes correctly."""
        manager = ContainerManager()
        assert manager.docker_client is not None
        assert isinstance(manager.sessions, dict)
        assert manager.image_name == "consol/rocky-xfce-vnc"
        assert manager.network_name == "agent-network"

        # Verify network check was performed
        mock_docker_client.networks.list.assert_called_with(names=["agent-network"])

    def test_ensure_network_creates_if_missing(self, mock_docker_client):
        """Test that _ensure_network creates a network if it doesn't exist."""
        # Setup network list to return empty list (network doesn't exist)
        mock_docker_client.networks.list.return_value = []

        manager = ContainerManager()
        manager.docker_client = mock_docker_client
        manager._ensure_network()

        # Verify create was called
        mock_docker_client.networks.create.assert_called_with(
            "agent-network", driver="bridge"
        )

    def test_ensure_network_skips_if_exists(self, mock_docker_client):
        """Test that _ensure_network doesn't create a network if it exists."""
        # Setup network list to return a network (network exists)
        mock_network = MagicMock()
        mock_docker_client.networks.list.return_value = [mock_network]

        manager = ContainerManager()
        manager.docker_client = mock_docker_client
        manager._ensure_network()

        # Verify create was not called
        mock_docker_client.networks.create.assert_not_called()

    @patch("uuid.uuid4")
    def test_create_session(self, mock_uuid, container_manager, mock_docker_client):
        """Test creating a new session."""
        # Mock UUID generation
        mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

        # Mock find_available_port to return predictable values
        container_manager._find_available_port = MagicMock()
        container_manager._find_available_port.side_effect = [5901, 6901]

        # Create a session
        session = container_manager.create_session("Test Session")

        # Verify container was created with correct parameters
        mock_docker_client.containers.run.assert_called_with(
            image=container_manager.image_name,
            name=ANY,
            detach=True,
            environment={
                "VNC_PW": "vncpassword",
                "VNC_RESOLUTION": "1280x800",
            },
            ports={
                "5901/tcp": 5901,
                "6901/tcp": 6901,
            },
            network=container_manager.network_name,
        )

        # Verify session details
        assert session["id"] == "12345678-1234-5678-1234-567812345678"
        assert session["name"] == "Test Session"
        assert session["container_id"] == "container123"
        assert session["vnc_port"] == 5901
        assert session["novnc_port"] == 6901
        assert session["status"] == "running"
        assert session["ai_control"] == "active"

        # Verify session was stored
        assert container_manager.sessions[session["id"]] == session

    def test_list_sessions(self, container_manager, mock_docker_client):
        """Test listing sessions."""
        # Add a test session
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }
        container_manager.sessions["test-session-1"] = test_session

        # List sessions
        sessions = container_manager.list_sessions()

        # Verify container status was checked
        mock_docker_client.containers.get.assert_called_with("container123")

        # Verify returned list
        assert len(sessions) == 1
        assert sessions[0] == test_session

        # Test with a non-existent container
        mock_docker_client.containers.get.side_effect = Exception("Container not found")
        sessions = container_manager.list_sessions()
        assert len(sessions) == 0

    def test_get_session(self, container_manager, mock_docker_client):
        """Test getting a specific session."""
        # Add a test session
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }
        container_manager.sessions["test-session-1"] = test_session

        # Get the session
        session = container_manager.get_session("test-session-1")

        # Verify container status was checked
        mock_docker_client.containers.get.assert_called_with("container123")

        # Verify returned session
        assert session == test_session

        # Test with a non-existent session
        assert container_manager.get_session("nonexistent") is None

        # Test with a session whose container no longer exists
        mock_docker_client.containers.get.side_effect = Exception("Container not found")
        assert container_manager.get_session("test-session-1") is None
        assert "test-session-1" not in container_manager.sessions

    def test_delete_session(self, container_manager, mock_docker_client):
        """Test deleting a session."""
        # Add a test session
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }
        container_manager.sessions["test-session-1"] = test_session

        # Delete the session
        success = container_manager.delete_session("test-session-1")

        # Verify container operations
        mock_docker_client.containers.get.assert_called_with("container123")
        mock_docker_client.containers.get.return_value.stop.assert_called_with(
            timeout=5
        )
        mock_docker_client.containers.get.return_value.remove.assert_called_with(
            force=True
        )

        # Verify success and session removal
        assert success
        assert "test-session-1" not in container_manager.sessions

        # Test with a non-existent session
        assert not container_manager.delete_session("nonexistent")

        # Test with container already removed
        container_manager.sessions["test-session-1"] = test_session
        mock_docker_client.containers.get.side_effect = Exception("Container not found")
        assert container_manager.delete_session("test-session-1")
        assert "test-session-1" not in container_manager.sessions

    def test_pause_resume_ai_control(self, container_manager):
        """Test pausing and resuming AI control."""
        # Add a test session
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }
        container_manager.sessions["test-session-1"] = test_session

        # Pause AI control
        assert container_manager.pause_ai_control("test-session-1")
        assert test_session["ai_control"] == "paused"

        # Resume AI control
        assert container_manager.resume_ai_control("test-session-1")
        assert test_session["ai_control"] == "active"

        # Test with a non-existent session
        assert not container_manager.pause_ai_control("nonexistent")
        assert not container_manager.resume_ai_control("nonexistent")

    def test_inject_instructions(self, container_manager):
        """Test injecting instructions to a session."""
        # Add a test session
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }
        container_manager.sessions["test-session-1"] = test_session

        # Inject instructions
        instructions = "Navigate to example.com and click on links about technology"
        assert container_manager.inject_instructions("test-session-1", instructions)
        assert test_session["last_instructions"] == instructions
        assert "last_instruction_time" in test_session

        # Test with a non-existent session
        assert not container_manager.inject_instructions("nonexistent", instructions)

    def test_find_available_port(self, container_manager):
        """Test finding an available port."""
        # Add a test session with ports
        test_session = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "status": "running",
        }
        container_manager.sessions["test-session-1"] = test_session

        # Find VNC port
        port = container_manager._find_available_port(5901, 5910)
        assert port != 5901  # Should not return the used port
        assert 5901 <= port <= 5910  # Should be in the range

        # Find noVNC port
        port = container_manager._find_available_port(6901, 6910)
        assert port != 6901  # Should not return the used port
        assert 6901 <= port <= 6910  # Should be in the range
