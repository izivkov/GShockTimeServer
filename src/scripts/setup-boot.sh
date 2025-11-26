#!/bin/bash

set -e
BOOT_SCRIPT="$HOME/onboot.sh"
LOG_DIR="$HOME/logs"

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
