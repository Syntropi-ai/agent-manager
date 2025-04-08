"""
Integration tests for the Agent Manager API.
"""

import json
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_container_manager():
    """Mock for the container manager."""
    with patch("agent_manager.orchestrator.app.container_manager") as mock:
        # Mock list_sessions to return a test session
        mock.list_sessions.return_value = [
            {
                "id": "test-session-1",
                "name": "Test Session",
                "container_id": "container123",
                "vnc_port": 5901,
                "novnc_port": 6901,
                "novnc_url": "http://localhost:6901/vnc.html",
                "status": "running",
                "ai_control": "active",
            }
        ]

        # Mock get_session to return a test session
        mock.get_session.return_value = {
            "id": "test-session-1",
            "name": "Test Session",
            "container_id": "container123",
            "vnc_port": 5901,
            "novnc_port": 6901,
            "novnc_url": "http://localhost:6901/vnc.html",
            "status": "running",
            "ai_control": "active",
        }

        # Mock create_session to return a new session
        mock.create_session.return_value = {
            "id": "test-session-2",
            "name": "New Session",
            "container_id": "container456",
            "vnc_port": 5902,
            "novnc_port": 6902,
            "novnc_url": "http://localhost:6902/vnc.html",
            "status": "running",
            "ai_control": "active",
        }

        # Mock other methods to return success
        mock.delete_session.return_value = True
        mock.pause_ai_control.return_value = True
        mock.resume_ai_control.return_value = True
        mock.inject_instructions.return_value = True

        yield mock


def test_get_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_get_sessions(client, mock_container_manager):
    """Test the get sessions API endpoint."""
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["id"] == "test-session-1"
    assert data[0]["name"] == "Test Session"


def test_get_session(client, mock_container_manager):
    """Test the get session API endpoint."""
    response = client.get("/api/sessions/test-session-1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == "test-session-1"
    assert data["name"] == "Test Session"

    # Test with nonexistent session
    mock_container_manager.get_session.return_value = None
    response = client.get("/api/sessions/nonexistent")
    assert response.status_code == 404


def test_create_session(client, mock_container_manager):
    """Test the create session API endpoint."""
    response = client.post(
        "/api/sessions",
        data=json.dumps({"name": "New Session"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == "test-session-2"
    assert data["name"] == "New Session"


def test_delete_session(client, mock_container_manager):
    """Test the delete session API endpoint."""
    response = client.delete("/api/sessions/test-session-1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"]

    # Test failure case
    mock_container_manager.delete_session.return_value = False
    response = client.delete("/api/sessions/test-session-1")
    assert response.status_code == 500


def test_pause_session(client, mock_container_manager):
    """Test the pause session API endpoint."""
    response = client.post("/api/sessions/test-session-1/pause")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"]

    # Test failure case
    mock_container_manager.pause_ai_control.return_value = False
    response = client.post("/api/sessions/test-session-1/pause")
    assert response.status_code == 500


def test_resume_session(client, mock_container_manager):
    """Test the resume session API endpoint."""
    response = client.post("/api/sessions/test-session-1/resume")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"]

    # Test failure case
    mock_container_manager.resume_ai_control.return_value = False
    response = client.post("/api/sessions/test-session-1/resume")
    assert response.status_code == 500


def test_inject_instructions(client, mock_container_manager):
    """Test the inject instructions API endpoint."""
    response = client.post(
        "/api/sessions/test-session-1/inject",
        data=json.dumps({"instructions": "Browse to example.com"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"]

    # Test without instructions
    response = client.post(
        "/api/sessions/test-session-1/inject",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400

    # Test failure case
    mock_container_manager.inject_instructions.return_value = False
    response = client.post(
        "/api/sessions/test-session-1/inject",
        data=json.dumps({"instructions": "Browse to example.com"}),
        content_type="application/json",
    )
    assert response.status_code == 500
