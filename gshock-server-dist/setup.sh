#!/bin/bash

echo "== G-Shock Server Installer for Raspberry Pi =="

# Update & upgrade
sudo apt update && sudo apt upgrade -y

# Install some tools
sudo apt install -y python3 python3-pip
sudo apt update
sudo apt install -y zip unzip

# Install dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create and enable systemd service
cat << EOL | sudo tee /etc/systemd/system/gshock.service > /dev/null
[Unit]
Description=G-Shock Server Python App
After=network.target bluetooth.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/gshock-server-dist
ExecStart=/usr/bin/python3 /home/pi/gshock-server-dist/gshock_server.py --multi-watch
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable gshock.service
sudo systemctl start gshock.service
# sudo systemctl status gshock.service
