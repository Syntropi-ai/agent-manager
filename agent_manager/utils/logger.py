"""
Logging configuration for the Agent Manager application.
Sets up logging with appropriate formatters and handlers.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: Optional[str] = None, log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Name for the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    name = name or "agent_manager"
    logger = logging.getLogger(name)

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create file handler
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
    os.makedirs(logs_dir, exist_ok=True)

    log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(os.path.join(logs_dir, log_filename))
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Create a root logger for the application
logger = setup_logger(
    "agent_manager", os.environ.get("AGENT_MANAGER_LOG_LEVEL", "INFO")
)
