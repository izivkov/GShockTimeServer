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
    sudo systemctl restart "$SERVICE_NAME"

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
