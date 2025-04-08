# Installation Guide

This guide walks you through the installation process for the Agent Manager system.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed:

1. **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
2. **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
3. **Docker Compose** - [Install Docker Compose](https://docs.docker.com/compose/install/)
4. **Git** (optional) - [Install Git](https://git-scm.com/downloads)

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-manager.git
cd agent-manager
```

### Step 2: Set Up Environment

Create a virtual environment and install the required dependencies:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### Step 3: Configure Environment Variables

Copy the example environment file and modify it according to your needs:

```bash
cp .env.example .env
```

Edit the `.env` file and set the required configuration variables, especially:

- `AGENT_MANAGER_SECRET_KEY`: Change this to a secure random string
- `AGENT_MANAGER_AI_API_KEY`: Your Anthropic API key (if using Claude)

### Step 4: Build and Start the Services

Use Docker Compose to build and start the services:

```bash
docker-compose up -d
```

The first time you run this command, Docker will download the required images and build the containers, which may take a few minutes.

### Step 5: Access the Dashboard

Once the services are running, you can access the dashboard at:

```
http://localhost:5000
```

## Manual Installation (Without Docker Compose)

If you prefer not to use Docker Compose, you can run the components separately:

### 1. Start a Redis instance:

```bash
docker run -d --name agent-redis -p 6379:6379 redis:alpine
```

### 2. Run the Agent Manager application:

```bash
# Make sure your virtual environment is activated
python -m agent_manager
```

## Verifying the Installation

To verify that your installation is working correctly:

1. Access the dashboard at `http://localhost:5000`
2. Create a new browser session
3. Verify that the session starts and you can see the browser via noVNC

## Troubleshooting

### Common Issues

#### Docker permission issues

If you encounter permission errors when running Docker commands, ensure your user is part of the `docker` group:

```bash
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

#### Port conflicts

If you see errors about ports already being in use, you can modify the port mappings in the `docker-compose.yml` file.

#### API key issues

If the AI functionality is not working, verify your API key in the `.env` file.

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the logs: `docker-compose logs`
2. Search for existing issues in the GitHub repository
3. Create a new issue if needed, providing detailed information about the problem