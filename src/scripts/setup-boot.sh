#!/bin/bash

set -e
BOOT_SCRIPT="$HOME/onboot.sh"
LOG_DIR="$HOME/logs"

#!/bin/bash

# Unblock all rfkill (WiFi, Bluetooth, etc.)
sudo rfkill unblock all

