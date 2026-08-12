#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/agent-config"
HOME_DIR="$TMP/home"
mkdir -p "$REPO" "$HOME_DIR"
cp -a \
  "$ROOT/install.sh" \
  "$ROOT/scripts" \
  "$ROOT/pi" \
  "$ROOT/claude" \
  "$ROOT/shared" \
  "$ROOT/machines" \
  "$ROOT/skills" \
  "$REPO/"

mkdir -p "$REPO/pi/agents"
printf '%s\n' '---' 'name: delegate' '---' > "$REPO/pi/agents/delegate.md"

printf '\n' | HOME="$HOME_DIR" "$REPO/install.sh" >/dev/null

target="$HOME_DIR/.pi/agent/agents"
[[ -L "$target" ]] || {
  printf 'expected pi agents symlink: %s\n' "$target" >&2
  exit 1
}
[[ "$(readlink "$target")" == "$REPO/pi/agents" ]] || {
  printf 'wrong pi agents target: %s -> %s\n' "$target" "$(readlink "$target")" >&2
  exit 1
}
[[ -f "$target/delegate.md" ]] || {
  printf 'installed delegate agent is missing: %s\n' "$target/delegate.md" >&2
  exit 1
}

printf 'pi agent installation passed\n'
