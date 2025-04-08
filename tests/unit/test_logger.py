"""
Unit tests for the logger module.
"""

import logging
from unittest.mock import patch, mock_open
from agent_manager.utils.logger import setup_logger


def test_setup_logger_creates_new_logger():
    """Test that setup_logger creates a new logger with the correct name."""
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level <= logging.INFO


def test_setup_logger_with_custom_level():
    """Test that setup_logger sets the correct log level."""
    logger = setup_logger("test_debug_logger", "DEBUG")
    assert logger.level == logging.DEBUG


def test_setup_logger_handlers():
    """Test that setup_logger adds the correct handlers."""
    logger = setup_logger("test_handlers_logger")

    # Should have at least two handlers (console and file)
    assert len(logger.handlers) >= 2

    # Check handler types
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types


@patch("os.path.dirname")
@patch("os.makedirs")
@patch("logging.FileHandler")
@patch("builtins.open", new_callable=mock_open)
def test_setup_logger_creates_logs_dir(
    mock_file_open, mock_file_handler, mock_makedirs, mock_dirname
):
    """Test that setup_logger creates the logs directory if it doesn't exist."""
    mock_dirname.return_value = "/fake/path"

    setup_logger("test_dir_logger")

    # Verify that os.makedirs was called with exist_ok=True
    mock_makedirs.assert_called_once()
    args, kwargs = mock_makedirs.call_args
    assert kwargs.get("exist_ok")


def test_setup_logger_formatter():
    """Test that setup_logger sets the correct formatter."""
    logger = setup_logger("test_formatter_logger")

    # Check that all handlers have a formatter
    for handler in logger.handlers:
        assert handler.formatter is not None

        # Check that the format string contains common logging elements
        format_str = handler.formatter._fmt
        assert "%(asctime)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(message)s" in format_str
