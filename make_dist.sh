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
[ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Create setup.sh with the desired content
cat << 'EOF' > "$DIST_DIR/setup.sh"
#!/bin/bash

echo "== G-Shock Server Installer for Raspberry Pi Zero =="

# Update & upgrade
sudo apt update && sudo apt upgrade -y

# Install some tools
sudo apt install -y python3-pip
sudo apt install -y zip unzip

# Setup virtual environmsnent
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo ""
echo "✅ Installation complete!"

# Create and enable systemd service
cat << EOL | sudo tee /etc/systemd/system/gshock.service > /dev/null
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=/home/pi/gshock-server-dist/venv/bin/python /home/pi/gshock-server-dist/gshock_server.py --multi-watch
WorkingDirectory=/home/pi/gshock-server-dist
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5
User=pi

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable gshock.service
sudo systemctl start gshock.service
# sudo systemctl status gshock.service
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