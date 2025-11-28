#!/bin/bash
set -x
set -e

# Change to the project root directory containing pyproject.toml and requirements.txt
cd "$(dirname "$0")"

# Update package list and install system dependencies needed for building Python packages
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y build-essential python3-dev python3-venv python3-pip curl libffi-dev

# Check if uv is installed, if not install it using the official install script
if ! command -v uv &> /dev/null
then
    echo "uv not found, installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Remove old or broken .venv directory to start fresh
rm -rf .venv

# Install dependencies from pyproject.toml using uv (creates .venv automatically)
uv sync

# Disable power-saving mode for the WiFi, otherwize it disconnects after some time.
echo 'sudo /sbin/iwconfig wlan0 power off' | sudo tee /etc/rc.local > /dev/null
echo ""
echo "✅ Installation complete!"

# Create and enable systemd service
SERVICE_FILE="/etc/systemd/system/gshock.service"
INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"

sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
Type=simple

# Run as your user (recommended)
User=$SERVICE_USER
WorkingDirectory=$HOME/gshock-server-dist
ExecStart=$HOME/.local/bin/uv run gshock_server.py
Environment=PYTHONUNBUFFERED=1

# Restart on crashes
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable gshock.service
sudo systemctl start gshock.service
echo "✅ gshock.service installed and started."
