FROM python:3.10-bullseye

# Install tools needed for development
RUN apt-get update && apt-get install -y \
    git \
    curl \
    sudo \
    bash \
    docker.io \
    docker-compose \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create vscode user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Add vscode user to docker group to allow docker commands
RUN usermod -aG docker $USERNAME

# Install Python dependencies
WORKDIR /workspaces/agent-manager
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN pip install --no-cache-dir black ruff mypy pytest pytest-cov

ENV PYTHONPATH=/workspaces/agent-manager

USER $USERNAME