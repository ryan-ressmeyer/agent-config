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
  "$ROOT/ponytail" \
  "$ROOT/shared" \
  "$ROOT/machines" \
  "$ROOT/skills" \
  "$REPO/"

HOME="$HOME_DIR" "$REPO/install.sh" </dev/null >/dev/null

CODEX_CONTEXT="$HOME_DIR/.codex/AGENTS.md"
[[ -f "$CODEX_CONTEXT" ]] || {
  printf 'Codex context was not generated: %s\n' "$CODEX_CONTEXT" >&2
  exit 1
}

cmp -s "$HOME_DIR/.pi/agent/AGENTS.md" "$CODEX_CONTEXT" || {
  printf 'Codex and pi contexts differ\n' >&2
  exit 1
}

printf 'Codex context installation passed\n'
