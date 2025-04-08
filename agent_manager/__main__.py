"""
Main entry point for the Agent Manager application.
"""

import sys
import os
import argparse

from agent_manager.orchestrator.app import app, socketio
from agent_manager.utils.config import config
from agent_manager.utils.logger import logger


def main():
    """
    Run the Agent Manager application.

    This is the main entry point for running the application.
    It parses command line arguments and starts the Flask server.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Agent Manager - Browser Automation Orchestrator"
    )
    parser.add_argument(
        "--host", default=config.get("HOST"), help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.get("PORT"),
        help="Port to bind the server to",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=config.get("DEBUG"),
        help="Enable debug mode",
    )

    args = parser.parse_args()

    logger.info(
        f"Starting Agent Manager on {args.host}:{args.port} (debug: {args.debug})"
    )

    try:
        # Start the Flask application with Socket.IO
        socketio.run(app, host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Add the package directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    main()
