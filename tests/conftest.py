"""
Test configuration for Agent Manager tests.
"""

import sys
import pytest
from pathlib import Path

# Add the project root to the path to enable imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# These imports need to be after the sys.path modification
import agent_manager.orchestrator.app as app_module  # noqa: E402
import agent_manager.utils.config as config_module  # noqa: E402


@pytest.fixture
def config():
    """Test configuration fixture."""
    return config_module.Config()


@pytest.fixture
def client():
    """Test client for the Flask application."""
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client
