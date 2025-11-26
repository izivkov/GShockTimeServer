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
if ! pip show spidev > /dev/null 2>&1; then
    echo "Installing Python spidev module..."
    uv pip install spidev
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
