#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() { printf '%s\n' "$1" >&2; exit 1; }
HOOK="$ROOT/claude/hooks/glim-context.sh"
HOME_DIR="$TMP/home"
SKILL="$HOME_DIR/.pi/agent/git/github.com/ryan-ressmeyer/glim/integrations/generic-skill/glim/SKILL.md"
mkdir -p "$(dirname "$SKILL")" "$TMP/bin" "$TMP/no-glim" "$TMP/no-jq" "$TMP/no-timeout"
printf 'Glimse instructions\n' >"$SKILL"

# Only glim is simulated; jq and timeout are the real installed binaries.
for tool in jq timeout; do ln -s "$(command -v "$tool")" "$TMP/bin/$tool"; done
printf '%s\n' '#!/bin/bash' \
  '[[ "$1" == status ]] || exit 2' \
  '[[ "${GLIM_DELAY:-}" == "" ]] || /bin/sleep "$GLIM_DELAY"' \
  'printf "%s" "${GLIM_RESPONSE:-}"' \
  'exit "${GLIM_EXIT:-0}"' >"$TMP/bin/glim"
chmod +x "$TMP/bin/glim"
for tool in jq timeout glim; do
  for missing in jq timeout glim; do
    [[ "$tool" == "$missing" ]] || ln -s "$TMP/bin/$tool" "$TMP/no-$missing/$tool"
  done
done

run_hook() {
  local path="$1" response="$2" expected="$3"
  shift 3
  HOME="$HOME_DIR" PATH="$path" GLIM_RESPONSE="$response" "$@" \
    /bin/bash "$HOOK" >"$TMP/stdout" 2>"$TMP/stderr" || fail "hook failed instead of exiting successfully"
  if [[ "$expected" == context ]]; then
    [[ "$(<"$TMP/stdout")" == *"$SKILL"* ]] || fail 'healthy context omitted absolute skill path'
    [[ "$(<"$TMP/stdout")" == *'visual'* && "$(<"$TMP/stdout")" == *'linked references'* ]] || fail 'healthy context omitted usage guidance'
    [[ "$(<"$TMP/stdout")" == *'diffs'* && "$(<"$TMP/stdout")" == *'logs'* ]] || fail 'healthy context omitted publishing exclusions'
  else
    [[ ! -s "$TMP/stdout" ]] || fail "unexpected hook output: $(<"$TMP/stdout")"
  fi
  [[ ! -s "$TMP/stderr" ]] || fail "hook wrote to stderr: $(<"$TMP/stderr")"
}

healthy='{"ok":true,"result":{"ok":true}}'
run_hook "$TMP/bin" "$healthy" context

rm "$SKILL"
run_hook "$TMP/bin" "$healthy" ""
printf 'Glimse instructions\n' >"$SKILL"
chmod 000 "$SKILL"
run_hook "$TMP/bin" "$healthy" ""
chmod 644 "$SKILL"
for missing in glim jq timeout; do
  run_hook "$TMP/no-$missing" "$healthy" ""
done
run_hook "$TMP/bin" "$healthy" "" /usr/bin/env GLIM_EXIT=1
for response in \
  '{"ok":false,"result":{"ok":true}}' \
  '{"ok":true,"result":{"ok":false}}' \
  '{"ok":true}' \
  'not-json' \
  '   ' \
  ''; do
  run_hook "$TMP/bin" "$response" ""
done
run_hook "$TMP/bin" "$healthy" "" /usr/bin/env GLIM_DELAY=4

printf 'Claude Glim context hook passed\n'
