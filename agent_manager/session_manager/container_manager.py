"""
Container Manager for handling browser sessions in Docker containers.
"""

import time
import uuid
from typing import Any, Dict, List, Optional

import docker


class ContainerManager:
    """
    Manages browser sessions running in Docker containers.
    Each container runs a VNC-enabled desktop environment with Chrome/Chromium.
    """

    def __init__(self) -> None:
        """Initialize the container manager with a Docker client."""
        self.docker_client = docker.from_env()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.image_name = "consol/rocky-xfce-vnc"  # Base image for browser sessions
        self.network_name = "agent-network"

        # Ensure our network exists
        self._ensure_network()

    def _ensure_network(self) -> None:
        """Ensure the Docker network exists."""
        networks = self.docker_client.networks.list(names=[self.network_name])
        if not networks:
            self.docker_client.networks.create(self.network_name, driver="bridge")

    def create_session(self, name: str) -> Dict[str, Any]:
        """
        Create a new browser session in a Docker container.

        Args:
            name: Name for the session

        Returns:
            Dict with session details
        """
        session_id = str(uuid.uuid4())
        container_name = f"agent-session-{session_id[:8]}"

        # Find available ports
        vnc_port = self._find_available_port(5901, 5910)
        novnc_port = self._find_available_port(6901, 6910)

        # Container configuration
        container = self.docker_client.containers.run(
            image=self.image_name,
            name=container_name,
            detach=True,
            environment={
                "VNC_PW": "vncpassword",  # Default VNC password
                "VNC_RESOLUTION": "1280x800",
            },
            ports={
                "5901/tcp": vnc_port,
                "6901/tcp": novnc_port,
            },
            network=self.network_name,
        )

        # Wait for container to be ready
        time.sleep(2)

        session = {
            "id": session_id,
            "name": name,
            "container_id": container.id,
            "container_name": container_name,
            "vnc_port": vnc_port,
            "novnc_port": novnc_port,
            "novnc_url": f"http://localhost:{novnc_port}/vnc.html?autoconnect=true",
            "status": "running",
            "ai_control": "active",
            "created_at": time.time(),
        }

        self.sessions[session_id] = session
        return session

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions.

        Returns:
            List of session details
        """
        # Update status for all sessions
        for session_id, session in list(self.sessions.items()):
            try:
                container = self.docker_client.containers.get(session["container_id"])
                session["status"] = container.status
            except Exception:
                # Container no longer exists or error occurred
                self.sessions.pop(session_id, None)

        return list(self.sessions.values())

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific session.

        Args:
            session_id: ID of the session to retrieve

        Returns:
            Session details or None if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        try:
            container = self.docker_client.containers.get(session["container_id"])
            session["status"] = container.status
            return session
        except Exception:
            # Container no longer exists or error occurred
            self.sessions.pop(session_id, None)
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Stop and remove a session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            container = self.docker_client.containers.get(session["container_id"])
            container.stop(timeout=5)
            container.remove(force=True)
            self.sessions.pop(session_id, None)
            return True
        except Exception:
            # Container already removed or error occurred
            # Remove session from tracking and return success
            self.sessions.pop(session_id, None)
            return True

    def pause_ai_control(self, session_id: str) -> bool:
        """
        Pause AI control for a session.

        Args:
            session_id: ID of the session to pause AI control

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            # In a real implementation, this would signal the AI controller to pause
            session["ai_control"] = "paused"
            return True
        except Exception:
            return False

    def resume_ai_control(self, session_id: str) -> bool:
        """
        Resume AI control for a session.

        Args:
            session_id: ID of the session to resume AI control

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            # In a real implementation, this would signal the AI controller to resume
            session["ai_control"] = "active"
            return True
        except Exception:
            return False

    def inject_instructions(self, session_id: str, instructions: str) -> bool:
        """
        Inject new instructions to the AI controller.

        Args:
            session_id: ID of the session to inject instructions
            instructions: New instructions for the AI

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            # In a real implementation, this would send instructions to the AI controller
            session["last_instructions"] = instructions
            session["last_instruction_time"] = time.time()
            return True
        except Exception:
            return False

    def _find_available_port(self, start_port: int, end_port: int) -> int:
        """
        Find an available port in the given range.

        Args:
            start_port: Start of port range
            end_port: End of port range

        Returns:
            Available port number
        """
        # Simple implementation - in production you would want to check if ports are actually free
        used_ports = set()
        for session in self.sessions.values():
            used_ports.add(session.get("vnc_port", 0))
            used_ports.add(session.get("novnc_port", 0))

        for port in range(start_port, end_port + 1):
            if port not in used_ports:
                return port

        # If no available port is found, return a default
        # In production, this should raise an exception
        return start_port
