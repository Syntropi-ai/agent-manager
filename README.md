# Agent Manager

## Python-Based Multi-Session Chrome + AI Orchestrator

Agent Manager is an open-source platform that allows you to launch, monitor, and control multiple remote Chrome browser sessions, each operated by an AI agent.

## Features

- Launch 2-5 concurrent Chrome sessions in remote environments (Docker containers)
- Monitor all sessions from a unified dashboard
- Live view and control via embedded noVNC web client
- Pause/Resume AI control for manual operation
- Inject new instructions to AI agents during operations

## Architecture

![Architecture Diagram](docs/architecture.png)

### Components

1. **Orchestrator Web Server**: Flask-based dashboard to manage sessions
2. **Session Manager**: Handles Chrome browser sessions in containers
3. **AI Controller**: Connects AI models to browser sessions
4. **VNC Integration**: Remote desktop access to each session

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-manager.git
cd agent-manager

# Install required dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Usage

```bash
# Start the orchestrator with Docker Compose
docker-compose up -d

# Access the dashboard
open http://localhost:5000
```

## Development

```bash
# Run tests
pytest

# Check code quality
ruff check .
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.