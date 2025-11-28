#!/bin/bash
set -euo pipefail

DIST_DIR="gshock-server-dist"
SRC_DIR="src/gshock-server"
SETUP_SCRIPT_DIR="src/scripts"

# Ensure dist directory exists and is a git repository
if [ ! -d "$DIST_DIR" ]; then
    echo "❌ Error: $DIST_DIR does not exist. Please clone the dist repository first."
    exit 1
fi

if [ ! -d "$DIST_DIR/.git" ]; then
    echo "❌ Error: $DIST_DIR is not a git repository."
    exit 1
fi

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
cp "$SRC_DIR"/display/pic/* "$DIST_DIR/display/pic/" 2>/dev/null || true
cp "$SETUP_SCRIPT_DIR"/*.sh "$DIST_DIR"
cp pyproject.toml "$DIST_DIR"

cp requirements.txt "$DIST_DIR/"
[ -f LICENSE ] && cp LICENSE "$DIST_DIR/"

# Make shell scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$DIST_DIR"/*.sh

# Write README
echo "📝 Writing README..."
cat <<'EOF' > "$DIST_DIR/README.md"
This repository holds distribution files for the `GShockTimeServer` project:
https://github.com/izivkov/GShockTimeServer
EOF

echo "📤 Committing and pushing..."

(
    cd "$DIST_DIR"
    git add -A

    git commit -m "Automated update from make-dist.sh on $(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
        || echo "No changes to commit."

    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "⬆️  Pushing branch '$CURRENT_BRANCH'..."
    git push origin "$CURRENT_BRANCH"

    # If tag argument supplied
    if [[ $# -ge 1 ]]; then
        TAG="$1"
        
        # Basic tag validation (optional: enforce semver)
        if [[ ! "$TAG" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
            echo "⚠️  Warning: Tag '$TAG' doesn't follow semantic versioning (e.g., v1.0.0)"
            read -p "Continue anyway? [y/N]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "❌ Tagging cancelled."
                exit 1
            fi
        fi
        
        echo "🏷️  Creating and pushing tag '$TAG'..."
        git tag -a "$TAG" -m "Release $TAG"
        git push origin "$TAG"
    else
        echo "ℹ️  No tag provided, only branch pushed."
    fi
)

echo "✅ Done. $DIST_DIR updated and pushed."
