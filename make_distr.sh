#!/bin/bash

set -e

DIST_DIR="dist_dir"

# Clean up previous output
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/display"

# Copy the two Python files
cp ./src/gshock_server.py "$DIST_DIR"
cp ./src/args.py "$DIST_DIR/"
cp ./src/display/*.py "$DIST_DIR/display/"

# Copy requirements.txt and optional extras
cp requirements.txt "$DIST_DIR/"
[ -f README.md ] && cp README.md "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Optional: zip it up
zip -r "${DIST_DIR}.zip" "$DIST_DIR"

echo "✅ Distribution created in $DIST_DIR/"

