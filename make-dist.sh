#!/bin/bash
set -euo pipefail

DIST_DIR="gshock-server-dist"
SRC_DIR="src/gshock-server"
SETUP_SCRIPT_DIR="src/scripts"

mkdir -p "$DIST_DIR"

echo "🔄 Cleaning dist repo..."
(
    cd "$DIST_DIR"
    git rm -rf . >/dev/null 2>&1 || true
    git clean -fdx
)

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$DIST_DIR"/display/{lib,pic}

# Copy Python and resource files
echo "📋 Copying source files..."
cp "$SRC_DIR"/*.py "$DIST_DIR"/
cp "$SRC_DIR"/display/*.py "$DIST_DIR/display/"
cp "$SRC_DIR"/display/lib/*.py "$DIST_DIR/display/lib/"
cp "$SRC_DIR"/display/pic/"*" "$DIST_DIR/display/pic/" 2>/dev/null || true
cp "$SETUP_SCRIPT_DIR"/*.sh "$DIST_DIR"
cp pyproject.toml "$DIST_DIR"
cp "$SRC_DIR"/display/pic/dw-b5600.png "$DIST_DIR/display/pic/"

cp requirements.txt "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Write README
echo "📝 Writing README..."
cat << 'EOF' > "$DIST_DIR/README.md"
This repository holds distribution files for the `GShockTimeServer` project:
https://github.com/izivkov/GShockTimeServer
EOF

echo "📤 Committing and pushing..."

(
    cd "$DIST_DIR"
    git add -A

    git commit -m "Automated update from make_dist.sh on $(date '+%Y-%m-%d %H:%M:%S')" \
        || echo "No changes to commit."

    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "⬆️  Pushing branch '$CURRENT_BRANCH'..."
    git push origin "$CURRENT_BRANCH"

    # If tag argument supplied
    if [[ $# -ge 1 ]]; then
        TAG="$1"
        echo "🏷️  Creating and pushing tag '$TAG'..."
        git tag -a "$TAG" -m "Release $TAG"
        git push origin "$TAG"
    else
        echo "ℹ️  No tag provided, only branch pushed."
    fi
)

echo "✅ Done. $DIST_DIR updated and pushed."
