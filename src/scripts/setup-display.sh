#!/bin/bash

# Installs all display-related dependencies. While installing, it will ask you to select the display type.
# Note: You need to run both setup.sh and setup-display.sh.

set -e
set -x

echo "== Display setup =="

INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"

# Update apt and install required system packages for building and runtime
sudo apt-get update
sudo apt-get install -y \
    python3-pip python3-venv python3-dev build-essential pkg-config unzip zip wget swig \
    libffi-dev libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7-dev \
    libtiff5-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    p7zip-full libopenblas-dev liblgpio-dev

# Ensure piwheels is enabled for pre-built binary wheels (usually enabled by default on Raspberry Pi OS)
if ! grep -q "extra-index-url=https://www.piwheels.org/simple" /etc/pip.conf; then
    echo "[global]" | sudo tee -a /etc/pip.conf
    echo "extra-index-url=https://www.piwheels.org/simple" | sudo tee -a /etc/pip.conf
fi

# Install display dependencies into the existing .venv
# We use 'uv pip install' to avoid modifying pyproject.toml on the device
$HOME/.local/bin/uv pip install --extra-index-url https://www.piwheels.org/simple spidev smbus smbus2 gpiozero numpy luma.oled luma.lcd lgpio pillow st7789 RPi.GPIO

DISPLAY_TYPE="waveshare"
echo "Display type set to: $DISPLAY_TYPE"

# Overwrite systemd service with display version
SERVICE_FILE="/etc/systemd/system/gshock.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
Type=simple

# Run as your user (recommended)
User=$SERVICE_USER
WorkingDirectory=$HOME/gshock-server-dist
ExecStart=$HOME/.local/bin/uv run gshock_server_display.py --display $DISPLAY_TYPE
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
