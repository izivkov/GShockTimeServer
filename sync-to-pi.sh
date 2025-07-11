#!/bin/bash

# === CONFIGURATION ===
LOCAL_DIR="/home/izivkov/projects/GShockTimeServer/gshock-server"           # Folder you're editing on PC
REMOTE_USER="pi"
REMOTE_HOST="pizero.local"                 # Replace with your Pi's IP
REMOTE_DIR="/home/pi/gshock-server-dist"   # Destination on the Pi

# === Ensure inotifywait is installed ===
if ! command -v inotifywait >/dev/null 2>&1; then
    echo "Please install inotify-tools: sudo apt install inotify-tools"
    exit 1
fi

echo "Watching $LOCAL_DIR for Python file changes. Press Ctrl+C to stop."

while true; do
    inotifywait -e modify,create,delete,move -r --format '%w%f' --exclude '(\.git|venv)' "$LOCAL_DIR" | while read changed; do
        printf "Detected change in: %s\n" "$changed"
        if [[ "$changed" == *.py ]]; then
            echo "Change detected in $changed. Syncing..."
            rsync -avz --delete --progress -e ssh \
            --include='*/' --include='*.py' --exclude='venv/' --exclude='.git/' --exclude='*' \
            --filter='P .git/' \
            "$LOCAL_DIR/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
              echo "Sync complete."
        fi
    done
done