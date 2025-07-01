#!/bin/bash

set -e

DIST_DIR="gshock-server-dist"

# Clean up previous output
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/display"

# Copy the two Python files
cp ./src/gshock_server.py "$DIST_DIR"
cp ./src/args.py "$DIST_DIR/"
cp ./src/display/*.py "$DIST_DIR/display/"

# Copy requirements.txt and optional extras
cp requirements.txt "$DIST_DIR/"
[ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Create setup.sh with the desired content
cat << 'EOF' > "$DIST_DIR/setup.sh"
#!/bin/bash

echo "== G-Shock Server Installer for Raspberry Pi Zero =="

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
WorkingDirectory=\$(pwd)
ExecStart=/usr/bin/python3 \$(pwd)/gshock_server.py --multi-watch
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable gshock.service
sudo systemctl start gshock.service
sudo systemctl status gshock.service
EOF

# Make setup.sh executable
chmod +x "$DIST_DIR/setup.sh"

echo "setup.sh has been created and made executable."

zip -r "${DIST_DIR}.zip" "$DIST_DIR"

echo "✅ Distribution created in $DIST_DIR/"
