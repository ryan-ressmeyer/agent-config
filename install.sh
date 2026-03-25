#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills"

if [ -L "$TARGET" ]; then
    echo "Symlink already exists: $TARGET -> $(readlink "$TARGET")"
    echo "To reinstall, remove it first: rm $TARGET"
    exit 0
elif [ -e "$TARGET" ]; then
    echo "Error: $TARGET already exists and is not a symlink."
    exit 1
fi

ln -s "$SKILLS_DIR" "$TARGET"
echo "Installed: $TARGET -> $SKILLS_DIR"
