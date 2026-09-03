#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/agent-config"
HOME_DIR="$TMP/home"
XDG_DIR="$TMP/xdg"
mkdir -p "$REPO" "$HOME_DIR" "$XDG_DIR"
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

HOME="$HOME_DIR" XDG_CONFIG_HOME="$XDG_DIR" "$REPO/install.sh" </dev/null >/dev/null

jq -e '.packages | index("git:github.com/DietrichGebert/ponytail@v4.9.0") != null' \
  "$HOME_DIR/.pi/agent/settings.json" >/dev/null || {
  printf 'pi settings do not declare the pinned Ponytail package\n' >&2
  exit 1
}
jq -e '
  .extraKnownMarketplaces.ponytail.source == {
    source: "github",
    repo: "DietrichGebert/ponytail",
    ref: "v4.9.0"
  }
  and .enabledPlugins["ponytail@ponytail"] == true
' "$HOME_DIR/.claude/settings.json" >/dev/null || {
  printf 'Claude settings do not declare and enable the pinned Ponytail plugin\n' >&2
  exit 1
}
jq -e '.defaultMode == "off"' "$XDG_DIR/ponytail/config.json" >/dev/null || {
  printf 'Ponytail default mode is not off\n' >&2
  exit 1
}
cmp -s "$REPO/ponytail/config.json" "$XDG_DIR/ponytail/config.json" || {
  printf 'deployed Ponytail config differs from tracked source\n' >&2
  exit 1
}

printf 'ponytail installation passed\n'
