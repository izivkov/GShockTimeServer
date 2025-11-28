#!/bin/bash

set -e
BOOT_SCRIPT="$HOME/onboot.sh"
LOG_DIR="$HOME/logs"

# Create the onboot.sh script
cat > "$BOOT_SCRIPT" <<'EOF'
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
sudo /usr/sbin/iw wlan0 set power_save off >> $HOME/boot.log 2>&1

sleep 10
sudo systemctl restart gshock.service >> $HOME/boot.log 2>&1
EOF

# Make the script executable
chmod +x "$BOOT_SCRIPT"

# Create systemd service to run onboot.sh at startup
SERVICE_FILE="/etc/systemd/system/onboot.service"
SERVICE_USER="$(whoami)"

sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=On Boot Script for G-Shock Server
After=network.target

[Service]
Type=oneshot
User=$SERVICE_USER
ExecStart=$BOOT_SCRIPT
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable onboot.service

echo "✅ onboot.sh created and onboot.service installed."
echo "The script will run on every boot to disable Wi-Fi power saving and restart gshock.service."
