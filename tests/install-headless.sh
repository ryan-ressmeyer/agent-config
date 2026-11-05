#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/agent-config"
HOME_DIR="$TMP/home"
mkdir -p "$REPO/.git/hooks" "$HOME_DIR"
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

[[ ! -e "$HOME_DIR/.pi/agent/auth.json" ]] || {
  printf 'headless install unexpectedly created auth.json\n' >&2
  exit 1
}

BLACKHOLE_SOURCE="$REPO/pi/pi-blackhole/pi-blackhole-config.json"
BLACKHOLE_TARGET="$HOME_DIR/.pi/agent/pi-blackhole/pi-blackhole-config.json"
[[ -f "$BLACKHOLE_TARGET" ]] || {
  printf 'headless install did not deploy Blackhole config\n' >&2
  exit 1
}
cmp -s "$BLACKHOLE_SOURCE" "$BLACKHOLE_TARGET" || {
  printf 'deployed Blackhole config differs from tracked source\n' >&2
  exit 1
}

[[ -L "$REPO/.git/hooks/pre-commit" ]] || {
  printf 'installer exited before completing the post-key steps\n' >&2
  exit 1
}

MODELS="$HOME_DIR/.pi/agent/models.json"
jq -e '.providers["openai-codex"].modelOverrides["gpt-6-astra"].contextWindow == 1050000' \
  "$MODELS" >/dev/null || {
  printf 'headless install did not set Astra context to 1050000\n' >&2
  exit 1
}

# Reinstallation updates the managed limit without replacing local configuration.
jq '
  .providers["openai-codex"].modelOverrides["gpt-6-astra"] |=
    (.contextWindow = 272000 | .maxTokens = 64000)
  | .providers.local = {baseUrl: "http://localhost:11434/v1"}
' "$MODELS" > "$TMP/models.json"
mv "$TMP/models.json" "$MODELS"
HOME="$HOME_DIR" "$REPO/install.sh" </dev/null >/dev/null
jq -e '
  .providers["openai-codex"].modelOverrides["gpt-6-astra"] ==
    {contextWindow: 1050000, maxTokens: 64000}
  and .providers.local == {baseUrl: "http://localhost:11434/v1"}
' "$MODELS" >/dev/null
cp "$MODELS" "$TMP/models-before.json"
HOME="$HOME_DIR" "$REPO/install.sh" </dev/null >/dev/null
cmp "$TMP/models-before.json" "$MODELS"

printf 'headless installation passed (Astra context, local settings, idempotence)\n'
