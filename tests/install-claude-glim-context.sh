#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { printf '%s\n' "$1" >&2; exit 1; }

REPO="$TMP/agent-config"
HOME_DIR="$TMP/home"
mkdir -p "$REPO" "$HOME_DIR/.claude/hooks"
cp -a "$ROOT/install.sh" "$ROOT/scripts" "$ROOT/pi" "$ROOT/claude" \
  "$ROOT/ponytail" "$ROOT/shared" "$ROOT/machines" "$ROOT/skills" "$REPO/"
printf 'user hook\n' >"$HOME_DIR/.claude/hooks/other.sh"

for iteration in 1 2; do
  HOME="$HOME_DIR" "$REPO/install.sh" </dev/null >/dev/null
  link="$HOME_DIR/.claude/hooks/glim-context.sh"
  [[ -L "$link" && "$(readlink "$link")" == "$REPO/claude/hooks/glim-context.sh" ]] ||
    fail 'Glim hook was not linked to the tracked script'
  [[ "$(<"$HOME_DIR/.claude/hooks/other.sh")" == 'user hook' ]] ||
    fail 'installer altered an unrelated hook'
  jq -e '
    .hooks.SessionStart == [{"hooks": [{
      "type": "command",
      "command": "bash \"$HOME/.claude/hooks/glim-context.sh\"",
      "timeout": 3
    }]}]
  ' "$HOME_DIR/.claude/settings.json" >/dev/null ||
    fail 'Claude SessionStart hook missing or duplicated'
done

printf 'Claude Glim hook installation passed\n'
