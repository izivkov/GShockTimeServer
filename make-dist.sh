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
cp pyproject.toml "$DIST_DIR/"

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

# G-Shock Server Installer for Raspberry Pi (headless, uv-native, systemd user service)

INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"
LAUNCHER="$HOME/.local/bin/start_gshock.sh"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$USER_SYSTEMD_DIR/gshock.service"

echo "== G-Shock Server Installer =="

# Ensure Python3 and Git are available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 is required. Please install Python3 first."
    exit 1
fi
if ! command -v git >/dev/null 2>&1; then
    echo "Git is required. Installing..."
    sudo apt-get update && sudo apt-get install -y git
fi

# Install uv if missing
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv globally..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "== Installing system dependencies for Pillow and other libs =="
sudo apt update
sudo apt install -y \
  build-essential python3-dev cython3 \
  libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
  libopenjp2-7-dev libtiff-dev libwebp-dev tcl-dev tk-dev \
  libdbus-1-dev libglib2.0-dev

# Install dependencies using uv
echo "== Installing dependencies via uv =="
cd "$INSTALL_DIR"
uv pip install numpy==1.26.4
uv sync -q

# Optional: disable WiFi power-saving
if command -v iwconfig >/dev/null 2>&1; then
    echo "Disabling WiFi power-saving..."
    sudo bash -c 'echo "/sbin/iwconfig wlan0 power off" >> /etc/rc.local'
else
    echo "Skipping WiFi power-saving (iwconfig not found)."
fi

# Create launcher script that runs server via uv
mkdir -p "$(dirname "$LAUNCHER")"
cat > "$LAUNCHER" <<EOL
#!/bin/bash
export PATH="\$HOME/.local/bin:\$PATH"
cd "$INSTALL_DIR"
uv run gshock_server.py
EOL
chmod +x "$LAUNCHER"

# Create systemd user service
mkdir -p "$USER_SYSTEMD_DIR"
cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=G-Shock Time Server
After=network.target

[Service]
ExecStart=$LAUNCHER
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOL

# Enable linger and start service
loginctl enable-linger "$SERVICE_USER"
systemctl --user daemon-reload
systemctl --user enable gshock.service
systemctl --user start gshock.service

echo "✅ G-Shock server installed and started via systemd user service."
echo "Manage with: systemctl --user status gshock.service"

EOF

chmod +x "$DIST_DIR/setup.sh"
echo "setup.sh has been created and made executable."

################################################################
# Create setup-boot.sh
################################################################
# run commands on boot

cat << 'EOF' > "$DIST_DIR/setup-boot.sh"
#!/bin/bash

set -e
BOOT_SCRIPT="$HOME/onboot.sh"
LOG_DIR="$HOME/logs"

tee "$BOOT_SCRIPT" > /dev/null <<EOL
#!/bin/bash

# Unblock all rfkill (WiFi, Bluetooth, etc.)
sudo rfkill unblock all

# Wait for wlan0 to be ready (max 20 seconds)
for i in {1..20}; do
    if /sbin/iw dev wlan0 info > /dev/null 2>&1; then
        echo "wlan0 detected."
        break
    fi
    echo "Waiting for wlan0... ($i)"
    sleep 1
done

# Run your commands here
echo "Disabling Wi-Fi power save"
sudo /usr/sbin/iw wlan0 set power_save off >> /home/pi/boot.log 2>&1

sleep 10
sudo systemctl restart gshock.service >> /home/pi/boot.log 2>&1

EOL

chmod +x "$BOOT_SCRIPT"

# Create and enable BOOT service
BOOT_SERVICE_FILE="/etc/systemd/system/user-boot-script.service"
sudo tee "$BOOT_SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=Run Pi user’s boot script
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/bin/bash -c "sudo -u pi /home/pi/onboot.sh"
Type=oneshot
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOL

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable user-boot-script.service
sudo systemctl start user-boot-script.service

EOF
chmod +x "$DIST_DIR/setup-boot.sh"

################################################################
# Create gshock-updater.sh
################################################################
cat << 'EOF' > "$DIST_DIR/gshock-updater.sh"
#!/bin/bash
set -e

# G-Shock Server Updater (uv-native)
# Pulls the latest GitHub release tag and restarts the systemd user service.

REPO_NAME="gshock-server-dist"
REPO_URL="https://github.com/izivkov/gshock-server-dist.git"
REPO_DIR="$HOME/$REPO_NAME"
LAST_TAG_FILE="$HOME/.config/gshock-updater/last-tag"
LOG_FILE="$HOME/logs/gshock-updater.log"
SERVICE_NAME="gshock.service"

mkdir -p "$(dirname "$LAST_TAG_FILE")" "$(dirname "$LOG_FILE")"

echo "== G-Shock Updater started at $(date) ==" >> "$LOG_FILE"

# Ensure dependencies exist
if ! command -v git >/dev/null 2>&1; then
    echo "Installing Git..." | tee -a "$LOG_FILE"
    sudo apt-get update && sudo apt-get install -y git
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv CLI..." | tee -a "$LOG_FILE"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Clone repo if missing
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Cloning repository..." | tee -a "$LOG_FILE"
    git clone --depth 1 "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# Fetch tags and determine latest
git fetch --tags --force
LATEST_TAG=$(git tag --sort=-v:refname | head -n 1)

if [ -z "$LATEST_TAG" ]; then
    echo "No tags found in repository." | tee -a "$LOG_FILE"
    exit 0
fi

# Read last synced tag
LAST_SYNCED_TAG=""
if [ -f "$LAST_TAG_FILE" ]; then
    LAST_SYNCED_TAG=$(cat "$LAST_TAG_FILE")
fi

# Update if a new tag is available
if [ "$LATEST_TAG" != "$LAST_SYNCED_TAG" ]; then
    echo "Updating to tag: $LATEST_TAG" | tee -a "$LOG_FILE"
    git reset --hard "$LATEST_TAG"
    git clean -fd
    echo "$LATEST_TAG" > "$LAST_TAG_FILE"

    echo "Installing/updating dependencies with uv..." | tee -a "$LOG_FILE"
    uv sync -q

    echo "Restarting G-Shock server user service..." | tee -a "$LOG_FILE"
    systemctl --user restart "$SERVICE_NAME"

    echo "✅ Updated to tag $LATEST_TAG at $(date)" | tee -a "$LOG_FILE"
else
    echo "Already up to date with tag: $LATEST_TAG" | tee -a "$LOG_FILE"
fi

# Ensure cron job is present for hourly updates
CRON_JOB="0 * * * * $REPO_DIR/gshock-updater.sh >> $LOG_FILE 2>&1"
( crontab -l 2>/dev/null | grep -Fv "$REPO_DIR/gshock-updater.sh" ; echo "$CRON_JOB" ) | crontab -

echo "Updater job installed in crontab (hourly check)." | tee -a "$LOG_FILE"
EOF

chmod +x "$DIST_DIR/gshock-updater.sh"
echo "gshock-updater has been created and made executable."

################################################################
# Create setup-display.sh
################################################################

cat << 'EOF' > "$DIST_DIR/setup-display.sh"
#!/bin/bash
set -e

# G-Shock Display Setup (headless, uv-native, systemd user service)

echo "== G-Shock Display Setup =="

INSTALL_DIR="$(cd "$(dirname "$0")"; pwd)"
SERVICE_USER="$(whoami)"
LAUNCHER="$HOME/.local/bin/start_gshock_display.sh"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$USER_SYSTEMD_DIR/gshock_display.service"

# Ensure Python and basic dependencies exist
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 is required. Please install it first."
    exit 1
fi

# Ensure uv CLI is installed (system-wide or user)
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv CLI..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Ensure system packages are available
echo "== Installing required system libraries =="
sudo apt-get update -qq
sudo apt install -y \
  build-essential python3-dev python3-numpy cython3 \
  libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
  libopenjp2-7-dev libtiff-dev libwebp-dev tcl-dev tk-dev \
  libdbus-1-dev libglib2.0-dev
  
sudo apt-get -y autoremove

# Sync display-related Python dependencies (auto env handled by uv)
echo "== Installing display-related Python packages with uv =="
uv sync --quiet
uv pip install spidev smbus smbus2 gpiozero numpy luma.oled luma.lcd lgpio pillow st7789 RPi.GPIO

# Ask user for display type
echo "Select your display type:"
echo "  1) waveshare (default)"
echo "  2) tft154"
read -p "Enter 1 or 2 [default: 1]: " DISPLAY_CHOICE

if [[ "$DISPLAY_CHOICE" != "2" ]]; then
    DISPLAY_TYPE="waveshare"
else
    DISPLAY_TYPE="tft154"
fi

echo "Display type set to: $DISPLAY_TYPE"

# Create launcher script
mkdir -p "$(dirname "$LAUNCHER")"
cat > "$LAUNCHER" <<EOL
#!/bin/bash
export PATH="\$HOME/.local/bin:\$PATH"
uv run "$INSTALL_DIR/gshock_server_display.py" --display $DISPLAY_TYPE
EOL
chmod +x "$LAUNCHER"

# Create systemd user service
mkdir -p "$USER_SYSTEMD_DIR"
cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=G-Shock Display Server
After=network.target

[Service]
ExecStart=$LAUNCHER
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOL

# Enable linger so the service runs without login
loginctl enable-linger "$SERVICE_USER"

# Enable and start the service
systemctl --user daemon-reload
systemctl --user enable gshock_display.service
systemctl --user start gshock_display.service

echo "✅ G-Shock display server installed and started (via systemd user service)."
echo "Manage with: systemctl --user status gshock_display.service"
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
. ./setup-boot.sh
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