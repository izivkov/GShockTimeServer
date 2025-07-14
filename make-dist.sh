#!/bin/bash

set -e

DIST_DIR="gshock-server-dist"
SRC_DIR="src/gshock-server"

# Clean submodule working tree but keep .git
cd "$DIST_DIR"
git rm -rf . > /dev/null 2>&1 || true
git clean -fdx
cd ..

mkdir -p "$DIST_DIR/display"
mkdir -p "$DIST_DIR/display/lib"
mkdir -p "$DIST_DIR/display/pic"

# Copy files
cp $SRC_DIR/*.py "$DIST_DIR"
cp $SRC_DIR/display/*.py "$DIST_DIR/display/"
cp $SRC_DIR/display/lib/*.py "$DIST_DIR/display/lib/"
cp $SRC_DIR/display/pic/* "$DIST_DIR/display/pic/"
cp requirements.txt "$DIST_DIR/"

[ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Create setup.sh with the desired content
cat << 'EOF' > "$DIST_DIR/setup.sh"
#!/bin/bash

set -e

INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"
VENV_DIR="$HOME/venv"

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

# Setup virtual environment in home directory
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Install dependencies
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "✅ Installation complete!"

# Create and enable systemd service
SERVICE_FILE="/etc/systemd/system/gshock.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/gshock_server.py --multi-watch
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

echo "✅ gshock.service installed and started."
EOF

chmod +x "$DIST_DIR/setup.sh"
echo "setup.sh has been created and made executable."

cat << 'EOF' > "$DIST_DIR/setup-display.sh"
#!/bin/bash

echo "== Display setup =="

# Update & upgrade
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv zip unzip \
    libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7-dev \
    libtiff5-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
    python3-tk p7zip-full wget

# Install Python packages
pip install --upgrade pip
pip install spidev smbus smbus2 gpiozero numpy luma.oled luma.lcd lgpio pillow st7789

echo "Select your display type:"
echo "  1) waveshare (default)"
echo "  2) ftp154"

read -t 180 -p "Enter 1 or 2 [default: 1]: " DISPLAY_CHOICE

# If timed out or invalid input, fall back to default
if [[ $? -ne 0 || "$DISPLAY_CHOICE" != "2" ]]; then
  DISPLAY_TYPE="waveshare"
else
  DISPLAY_TYPE="ftp154"
fi

# Overwrite systemd service with display version
SERVICE_FILE="/etc/systemd/system/gshock.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/gshock_server_display.py --multi-watch --display $DISPLAY_TYPE
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

echo "✅ Display setup complete!"
EOF
chmod +x "$DIST_DIR/setup-display.sh"
echo "setup-display.sh has been created and made executable."

cat << 'EOF' > "$DIST_DIR/enable-spi.sh"
#!/bin/bash

echo "== Enabling SPI interface =="

CONFIG_FILE="/boot/firmware/config.txt"
SPI_LINE="dtparam=spi=on"
REBOOT_NEEDED=false

# Check if SPI line exists
if grep -q "^$SPI_LINE" "$CONFIG_FILE"; then
    echo "SPI is already enabled."
else
    if grep -q "^#\s*$SPI_LINE" "$CONFIG_FILE"; then
        echo "Uncommenting SPI line..."
        sudo sed -i "s/^#\s*$SPI_LINE/$SPI_LINE/" "$CONFIG_FILE"
    else
        echo "Adding SPI line..."
        echo "$SPI_LINE" | sudo tee -a "$CONFIG_FILE" > /dev/null
    fi
    REBOOT_NEEDED=true
fi

# Check if spidev is installed
if ! pip3 show spidev > /dev/null 2>&1; then
    echo "Installing Python spidev module..."
    pip3 install spidev
else
    echo "Python spidev module already installed."
fi

if $REBOOT_NEEDED; then
    echo "SPI enabled. Reboot is required."
    read -p "Reboot now? [Y/n]: " choice
    case "$choice" in
        [nN]*) echo "Please reboot manually later." ;;
        *) echo "Rebooting..."; sudo reboot ;;
    esac
else
    echo "No changes made. No reboot needed."
fi
echo "== SPI setup complete! =="
EOF
chmod +x "$DIST_DIR/enable-spi.sh"
echo "enable-spi.sh has been created and made executable."

cat << 'EOF' > "$DIST_DIR/setup-all.sh"
#!/bin/bash
. ./setup.sh
. ./setup-display.sh
. ./enable-spi.sh
EOF
chmod +x "$DIST_DIR/setup-all.sh"
echo "setup-all.sh has been created and made executable."

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