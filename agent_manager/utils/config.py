"""
Configuration management for the Agent Manager application.
Loads configuration from environment variables and provides defaults.
"""

import os
from typing import Any, Dict, Union


class Config:
    """Configuration manager for the Agent Manager application."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.config: Dict[str, Any] = {
            # Web server settings
            "HOST": os.environ.get("AGENT_MANAGER_HOST", "0.0.0.0"),
            "PORT": int(os.environ.get("AGENT_MANAGER_PORT", 5000)),
            "DEBUG": os.environ.get("AGENT_MANAGER_DEBUG", "False").lower()
            in ("true", "1", "t"),
            "SECRET_KEY": os.environ.get("AGENT_MANAGER_SECRET_KEY", "dev_secret_key"),
            # Docker settings
            "DOCKER_BASE_URL": os.environ.get(
                "AGENT_MANAGER_DOCKER_URL", "unix://var/run/docker.sock"
            ),
            "BASE_IMAGE": os.environ.get(
                "AGENT_MANAGER_BASE_IMAGE", "consol/rocky-xfce-vnc"
            ),
            "NETWORK_NAME": os.environ.get(
                "AGENT_MANAGER_NETWORK_NAME", "agent-network"
            ),
            # VNC settings
            "VNC_PASSWORD": os.environ.get("AGENT_MANAGER_VNC_PASSWORD", "vncpassword"),
            "VNC_RESOLUTION": os.environ.get(
                "AGENT_MANAGER_VNC_RESOLUTION", "1280x800"
            ),
            "VNC_PORT_RANGE": (
                int(os.environ.get("AGENT_MANAGER_VNC_PORT_MIN", 5901)),
                int(os.environ.get("AGENT_MANAGER_VNC_PORT_MAX", 5910)),
            ),
            "NOVNC_PORT_RANGE": (
                int(os.environ.get("AGENT_MANAGER_NOVNC_PORT_MIN", 6901)),
                int(os.environ.get("AGENT_MANAGER_NOVNC_PORT_MAX", 6910)),
            ),
            # Redis settings for pub/sub
            "REDIS_HOST": os.environ.get("AGENT_MANAGER_REDIS_HOST", "redis"),
            "REDIS_PORT": int(os.environ.get("AGENT_MANAGER_REDIS_PORT", 6379)),
            "REDIS_DB": int(os.environ.get("AGENT_MANAGER_REDIS_DB", 0)),
            # AI settings
            "AI_API_KEY": os.environ.get("AGENT_MANAGER_AI_API_KEY", ""),
            "AI_MODEL": os.environ.get(
                "AGENT_MANAGER_AI_MODEL", "claude-3-opus-20240229"
            ),
            "AI_MAX_RETRIES": int(os.environ.get("AGENT_MANAGER_AI_MAX_RETRIES", 3)),
            # Session settings
            "MAX_SESSIONS": int(os.environ.get("AGENT_MANAGER_MAX_SESSIONS", 5)),
        }

        # Load any additional environment variables with the AGENT_MANAGER_ prefix
        self._load_from_environment()

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        prefix = "AGENT_MANAGER_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :]
                # Only add if not already defined
                if config_key not in self.config:
                    # Try to convert to appropriate type
                    self.config[config_key] = self._convert_value_type(value)

    def _convert_value_type(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert string value to appropriate type.

        Args:
            value: String value to convert

        Returns:
            Converted value (int, float, bool, or string)
        """
        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Handle boolean values
        if value.lower() in ("true", "1", "t"):
            return True
        elif value.lower() in ("false", "0", "f"):
            return False

        # Default to string
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            The configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.

        Args:
            key: Configuration key

        Returns:
            The configuration value

        Raises:
            KeyError: If the key is not found
        """
        if key not in self.config:
            raise KeyError(f"Configuration key '{key}' not found")
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dictionary syntax.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key

        Returns:
            True if the key exists, False otherwise
        """
        return key in self.config


# Create a singleton instance
config = Config()
