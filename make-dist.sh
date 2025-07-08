#!/bin/bash

set -e

DIST_DIR="gshock-server-dist"
SRC_DIR="gshock-server"

# Clean submodule working tree but keep .git
cd "$DIST_DIR"
git rm -rf . > /dev/null 2>&1 || true
git clean -fdx
cd ..

mkdir -p "$DIST_DIR/display"

# Copy files
cp $SRC_DIR/gshock_server.py "$DIST_DIR"
cp $SRC_DIR/args.py "$DIST_DIR/"
cp $SRC_DIR/display/*.py "$DIST_DIR/display/"
cp requirements.txt "$DIST_DIR/"

cp enable-spi.sh "$DIST_DIR/"
cp setup-display.sh "$DIST_DIR/"

[ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Create setup.sh with the desired content

cat << 'EOF' > "$DIST_DIR/setup.sh"
#!/bin/bash

set -e

INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"

echo "== G-Shock Server Installer for Linux =="

# Update & upgrade
if command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3-pip python3-venv zip unzip \
        libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7-dev \
        libtiff5-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3-pip python3-venv zip unzip
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3-pip python3-venv zip unzip
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python-pip python-virtualenv zip unzip
fi

# Setup virtual environment
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"

# Create and enable systemd service
SERVICE_FILE="/etc/systemd/system/gshock.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/gshock_server.py --multi-watch
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5
User=$SERVICE_USER

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable gshock.service
sudo systemctl start gshock.service
# sudo systemctl status gshock.service

echo "✅ gshock.service installed and started."
EOF

chmod +x "$DIST_DIR/setup.sh"
echo "setup.sh has been created and made executable."

# Commit and push in the submodule
cd "$DIST_DIR"
git add .
git commit -m "Automated update from make_dist.sh on $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit."
if [ -n "$1" ]; then
    git tag "$1"
    git push origin "$1"
fi
git push
cd ..

echo "✅ $DIST_DIR updated and pushed to remote."