# Agent Manager Architecture

## High-Level Design

Agent Manager is a Python-based platform designed to launch, monitor, and control multiple remote Chrome browser sessions, each operated by an AI agent. The core concept of the project is to provide a unified interface for managing browser sessions and integrating AI models to automate browser interactions.

### Core Concept

The core concept of Agent Manager is to create a system that allows users to manage multiple browser sessions remotely, with each session being controlled by an AI agent. This enables automated browsing, data extraction, and interaction with web applications without manual intervention.

## Key Components

### 1. Orchestrator Web Server

The orchestrator is a Flask-based web application that provides a dashboard for users to manage browser sessions. It handles:

- Creating and managing browser sessions
- Displaying session status and information
- Providing a user interface for controlling sessions
- Embedding noVNC clients for direct visual access to browser sessions

### 2. Session Manager

The session manager component is responsible for:

- Creating and managing Docker containers for browser sessions
- Allocating ports for VNC and noVNC connections
- Monitoring session status
- Handling container lifecycle (start, stop, pause, resume)

### 3. AI Controller

The AI controller connects AI models to browser sessions, allowing AI agents to control the browser. It provides:

- Connection to AI models via API
- Interpretation of AI instructions into browser actions
- Reading of browser content for AI decision-making
- Pause/resume functionality for AI control

### 4. VNC Integration

Each browser session runs in a Docker container with:

- A virtual desktop environment (Xfce)
- Chrome/Chromium web browser
- VNC server for remote access
- noVNC web client for browser-based access

## Architecture Diagram

```
+-------------------+      +-------------------+
|                   |      |                   |
|  Web Dashboard    |<---->|  Orchestrator     |
|  (Browser)        |      |  (Flask)          |
|                   |      |                   |
+-------------------+      +--------+----------+
                                    |
                                    v
+-------------------+      +-------------------+      +-------------------+
|                   |      |                   |      |                   |
|  AI Models        |<---->|  AI Controller    |<---->|  Session Manager  |
|  (Claude API)     |      |  (Python)         |      |  (Docker API)     |
|                   |      |                   |      |                   |
+-------------------+      +-------------------+      +--------+----------+
                                                               |
                                                               v
                              +-------------------+      +-------------------+
                              |                   |      |                   |
                              |  Browser Session  |<---->|  VNC/noVNC        |
                              |  (Chrome)         |      |  (Remote Access)  |
                              |                   |      |                   |
                              +-------------------+      +-------------------+
```

## Data Flow

1. **User Interaction:**
   - User accesses the web dashboard
   - Creates, monitors, and controls browser sessions
   - Views live browser sessions via embedded noVNC

2. **Session Creation:**
   - Orchestrator requests a new session from Session Manager
   - Session Manager creates a Docker container with VNC and Chrome
   - Container starts and exposes VNC/noVNC ports

3. **AI Control:**
   - AI Controller connects to the browser session
   - Reads page content and sends it to AI model
   - Interprets AI decisions and controls the browser
   - Can be paused for manual user control

## Technology Stack

- **Backend:** Python 3.9+, Flask, Socket.IO
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Containers:** Docker, consol/rocky-xfce-vnc base image
- **AI Integration:** Anthropic Claude API (extensible for other models)
- **Remote Access:** VNC, noVNC web client

## Configuration

The system is configured through environment variables, which are documented in the `.env.example` file.

## Security Considerations

- VNC connections are password-protected
- API keys are managed through environment variables
- Docker container isolation provides session separation
