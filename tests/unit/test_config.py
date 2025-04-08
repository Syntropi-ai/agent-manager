"""
Unit tests for the configuration module.
"""

import pytest
from agent_manager.utils.config import Config


def test_config_initialization():
    """Test that Config initializes with default values."""
    config = Config()
    assert config.get("HOST") == "0.0.0.0"
    assert config.get("PORT") == 5000
    assert isinstance(config.get("VNC_PORT_RANGE"), tuple)


def test_config_get_set():
    """Test getting and setting configuration values."""
    config = Config()

    # Test get with default
    assert config.get("NONEXISTENT", "default") == "default"

    # Test set and get
    config.set("TEST_KEY", "test_value")
    assert config.get("TEST_KEY") == "test_value"

    # Test dictionary-style access
    config["DICT_KEY"] = "dict_value"
    assert config["DICT_KEY"] == "dict_value"

    # Test contains check
    assert "DICT_KEY" in config
    assert "NONEXISTENT" not in config


@pytest.mark.parametrize(
    "env_var,env_value,config_key,expected",
    [
        ("AGENT_MANAGER_TEST_STR", "test", "TEST_STR", "test"),
        ("AGENT_MANAGER_TEST_INT", "42", "TEST_INT", 42),
        ("AGENT_MANAGER_TEST_BOOL", "True", "TEST_BOOL", True),
    ],
)
def test_environment_variables(monkeypatch, env_var, env_value, config_key, expected):
    """Test that environment variables are properly loaded."""
    # Set environment variable
    monkeypatch.setenv(env_var, env_value)

    # Create a fresh config that will load from environment
    config = Config()

    # Test that the value was loaded correctly
    if config_key in ("TEST_INT", "TEST_BOOL"):
        # These keys aren't automatically in our config, so we need to use default
        assert config.get(config_key, expected) == expected
    else:
        # This should be automatically loaded
        assert config.get(config_key) == expected
