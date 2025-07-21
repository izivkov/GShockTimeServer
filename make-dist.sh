#!/bin/bash

set -e

DIST_DIR="gshock-server-dist"
SRC_DIR="src/gshock-server"

mkdir -p "$DIST_DIR/"

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

# [ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

################################################################
# Create README.md
################################################################
cat << 'EOF' > "$DIST_DIR/README.md"
This repostory is used to hold the distribution files for `GShockTimeServer` repository:
https://github.com/izivkov/GShockTimeServer
EOF

################################################################
# Create setup.sh
################################################################
cat << 'EOF' > "$DIST_DIR/setup.sh"
#!/bin/bash

set -e

# This script installs the basic software, dependencies, sets up a service to start the server each time 
# the device is rebooted, etc. For a device with no display, this is sufficient to run the server.

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
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/gshock_server.py
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

################################################################
# Create gshock-updater.sh
################################################################
cat << 'EOF' > "$DIST_DIR/gshock-updater.sh"
#!/bin/bash

set -e

# This script will set the device to automatically update its software if a new version is available on GitHub.
# It will then restart the server, so you will always be running the latest version. The scripts sets us a cron job to
# run periodically and check for new tags on the `gshock-server-dist` GitHub repository.

set -e

REPO_NAME="gshock-server-dist"
REPO_URL="https://github.com/izivkov/gshock-server-dist.git"
REPO_DIR="$HOME/$REPO_NAME"
LAST_TAG_FILE="$HOME/.config/gshock-updater/last-tag"
LOG_FILE="$HOME/logs/gshock-updater.log"

mkdir -p "$(dirname "$LAST_TAG_FILE")"
mkdir -p "$(dirname "$LOG_FILE")"

# Clone repo if missing
if [ ! -d "$REPO_DIR/.git" ]; then
    git clone --depth 1 "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# Fetch tags and determine latest
git fetch --tags --force
LATEST_TAG=$(git tag --sort=-v:refname | head -n 1)

if [ -z "$LATEST_TAG" ]; then
    echo "No tags found in repository."
    exit 1
fi

# Read last synced tag
LAST_SYNCED_TAG=""
if [ -f "$LAST_TAG_FILE" ]; then
    LAST_SYNCED_TAG=$(cat "$LAST_TAG_FILE")
fi

# Update if a new tag is found
if [ "$LATEST_TAG" != "$LAST_SYNCED_TAG" ]; then
    echo "Updating to tag: $LATEST_TAG"
    git reset --hard "$LATEST_TAG"
    git clean -fd
    echo "$LATEST_TAG" > "$LAST_TAG_FILE"

    echo "Restarting gshock.service"
    sudo systemctl restart gshock.service
else
    echo "Already up to date with tag: $LATEST_TAG"
fi

# Ensure cron job is present
CRON_JOB="*/60 * * * * $REPO_DIR/gshock-updater.sh >> $LOG_FILE 2>&1"
( crontab -l 2>/dev/null | grep -Fv "$REPO_NAME/gshock-updater.sh" ; echo "$CRON_JOB" ) | crontab -
EOF

chmod +x "$DIST_DIR/gshock-updater.sh"
echo "gshock-updater has been created and made executable."

################################################################
# Create setup-display.sh
################################################################

cat << 'EOF' > "$DIST_DIR/setup-display.sh"
#!/bin/bash

# Installs all display-related dependencies. While installing, it will ask you to select the display type.
# Note: You need to run both setup.sh and setup-display.sh.

set -e

echo "== Display setup =="

# Update & upgrade
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv zip unzip \
    libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7-dev \
    libtiff5-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
    python3-tk p7zip-full wget

# Install Python packages
pip install --upgrade pip
pip install spidev smbus smbus2 gpiozero numpy luma.oled luma.lcd lgpio pillow st7789 RPi.GPIO

echo "Select your display type:"
echo "  1) waveshare (default)"
echo "  2) tft154"

read -p "Enter 1 or 2 [default: 1]: " DISPLAY_CHOICE

# If timed out or invalid input, fall back to default
if [[ "$DISPLAY_CHOICE" != "2" ]]; then
  DISPLAY_TYPE="waveshare"
else
  DISPLAY_TYPE="tft154"
fi

# Update config.ini with the selected display type
CONFIG_FILE="./config.ini"

# Validate DISPLAY_TYPE
case "$DISPLAY_TYPE" in
    waveshare|tft154|mock)
        ;;
    *)
        echo "Error: DISPLAY_TYPE must be one of: waveshare, tft154, mock"
        exit 1
        ;;
esac

echo "Display type set to: $DISPLAY_TYPE"

echo "[main]" > "$CONFIG_FILE"
echo "display = $DISPLAY_TYPE" >> "$CONFIG_FILE"
echo excluded_watches = '["OCW-S400-2AJF", "OCW-S400SG-2AJR", "OCW-T200SB-1AJF", "ECB-30", "ECB-20", "ECB-10", "ECB-50", "ECB-60", "ECB-70"]' >> "$CONFIG_FILE"

# end of config.ini update

# Overwrite systemd service with display version
SERVICE_FILE="/etc/systemd/system/gshock.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/gshock_server_display.py
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

################################################################
# Create enable-spi.sh
################################################################
cat << 'EOF' > "$DIST_DIR/enable-spi.sh"
#!/bin/bash

# This script will enable the Linux driver needed for the display. Without this step, the display will not work.
# Reboot when asked after the script runs.

set -e

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

# This script runs all setup scripts in order.

. ./setup.sh
. ./setup-display.sh
. ./gshock-updater.sh
. ./enable-spi.sh
EOF
chmod +x "$DIST_DIR/setup-all.sh"
echo "setup-all.sh has been created and made executable."

# Commit and push in the submodule
cd "$DIST_DIR"
git add .
git commit -m "Automated update from make_dist.sh on $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit."
# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push current branch
echo "Pushing branch '$CURRENT_BRANCH'..."
git push origin "$CURRENT_BRANCH"

# If a tag is provided, create and push it
if [ -n "$1" ]; then
    TAG="$1"
    echo "Creating and pushing tag '$TAG'..."
    git tag -a "$TAG" -m "Release $TAG"
    git push origin "$TAG"
else
    echo "No tag provided, only branch pushed."
fi

echo "✅ $DIST_DIR updated and pushed to remote."