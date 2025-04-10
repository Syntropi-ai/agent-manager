"""
Orchestrator web application for managing browser sessions.
"""

import os
from typing import Any

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

from agent_manager.session_manager.container_manager import ContainerManager

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
socketio = SocketIO(app)

# Initialize the container manager
container_manager = ContainerManager()


@app.route("/")
def index() -> str:
    """Render the dashboard homepage."""
    return render_template("index.html")


@app.route("/api/sessions", methods=["GET"])
def get_sessions() -> Any:
    """Get all active sessions."""
    sessions = container_manager.list_sessions()
    return jsonify(sessions)


@app.route("/api/sessions", methods=["POST"])
def create_session() -> Any:
    """Create a new browser session."""
    data = request.json or {}
    name = data.get("name", f"session-{len(container_manager.list_sessions()) + 1}")
    session = container_manager.create_session(name)
    return jsonify(session)


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str) -> Any:
    """Get details for a specific session."""
    session = container_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id: str) -> Any:
    """Stop and remove a session."""
    success = container_manager.delete_session(session_id)
    if not success:
        return jsonify({"error": "Failed to delete session"}), 500
    return jsonify({"success": True})


@app.route("/api/sessions/<session_id>/pause", methods=["POST"])
def pause_session(session_id: str) -> Any:
    """Pause AI control for a session."""
    success = container_manager.pause_ai_control(session_id)
    if not success:
        return jsonify({"error": "Failed to pause session"}), 500
    return jsonify({"success": True})


@app.route("/api/sessions/<session_id>/resume", methods=["POST"])
def resume_session(session_id: str) -> Any:
    """Resume AI control for a session."""
    success = container_manager.resume_ai_control(session_id)
    if not success:
        return jsonify({"error": "Failed to resume session"}), 500
    return jsonify({"success": True})


@app.route("/api/sessions/<session_id>/inject", methods=["POST"])
def inject_instructions(session_id: str) -> Any:
    """Inject new instructions to the AI controller."""
    data = request.json or {}
    instructions = data.get("instructions")
    if not instructions:
        return jsonify({"error": "Instructions are required"}), 400

    success = container_manager.inject_instructions(session_id, instructions)
    if not success:
        return jsonify({"error": "Failed to inject instructions"}), 500
    return jsonify({"success": True})


@socketio.on("connect")
def handle_connect() -> None:
    """Handle client connection to socket."""
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect() -> None:
    """Handle client disconnection from socket."""
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
