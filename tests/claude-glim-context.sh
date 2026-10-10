#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() { printf '%s\n' "$1" >&2; exit 1; }
HOOK="$ROOT/claude/hooks/glim-context.sh"
HOME_DIR="$TMP/home"
SOURCE="$HOME_DIR/.pi/agent/git/github.com/ryan-ressmeyer/glim/integrations/generic-skill/glim"
SKILL="$SOURCE/SKILL.md"
LINK="$HOME_DIR/.claude/skills/glim"
mkdir -p "$SOURCE/references" "$TMP/bin" "$TMP/no-glim" "$TMP/no-jq" "$TMP/no-timeout"
printf 'Glimse instructions\n' >"$SKILL"
printf 'Bundled reference\n' >"$SOURCE/references/usage.md"

# Only glim is simulated; jq, timeout and file utilities are real binaries.
for tool in jq timeout mkdir ln rm readlink; do ln -s "$(command -v "$tool")" "$TMP/bin/$tool"; done
printf '%s\n' '#!/bin/bash' \
  '[[ "$1" == status ]] || exit 2' \
  '[[ "${GLIM_DELAY:-}" == "" ]] || /bin/sleep "$GLIM_DELAY"' \
  'printf "%s" "${GLIM_RESPONSE:-}"' \
  'exit "${GLIM_EXIT:-0}"' >"$TMP/bin/glim"
chmod +x "$TMP/bin/glim"
for missing in jq timeout glim; do
  for tool in jq timeout glim mkdir ln rm readlink; do
    [[ "$tool" == "$missing" ]] || ln -s "$TMP/bin/$tool" "$TMP/no-$missing/$tool"
  done
done

run_hook() {
  local path="$1" response="$2" stderr_expected="${3:-quiet}"
  shift 3
  HOME="$HOME_DIR" PATH="$path" GLIM_RESPONSE="$response" "$@" \
    /bin/bash "$HOOK" >"$TMP/stdout" 2>"$TMP/stderr" || fail "hook failed instead of exiting successfully"
  [[ "$(<"$TMP/stdout")" == '{"hookSpecificOutput":{"hookEventName":"SessionStart","reloadSkills":true}}' ]] ||
    fail "hook did not emit reloadSkills JSON: $(<"$TMP/stdout")"
  "$TMP/bin/jq" -e '.hookSpecificOutput.hookEventName == "SessionStart" and .hookSpecificOutput.reloadSkills == true' \
    "$TMP/stdout" >/dev/null || fail 'hook emitted invalid JSON'
  if [[ "$stderr_expected" == conflict ]]; then
    [[ "$(<"$TMP/stderr")" == *"$LINK"* ]] || fail 'conflict not reported'
  else
    [[ ! -s "$TMP/stderr" ]] || fail "hook wrote to stderr: $(<"$TMP/stderr")"
  fi
}

owned() {
  [[ -L "$LINK" && "$(readlink "$LINK")" == "$SOURCE" ]] || fail 'owned skill symlink missing or wrong target'
  [[ "$(<"$LINK/references/usage.md")" == 'Bundled reference' ]] || fail 'bundled reference inaccessible'
}
absent() { [[ ! -e "$LINK" && ! -L "$LINK" ]] || fail 'owned skill link was not removed'; }

healthy='{"ok":true,"result":{"ok":true}}'
run_hook "$TMP/bin" "$healthy" quiet
owned
run_hook "$TMP/bin" "$healthy" quiet
owned

rm "$SKILL"
run_hook "$TMP/bin" "$healthy" quiet
absent
printf 'Glimse instructions\n' >"$SKILL"
run_hook "$TMP/bin" "$healthy" quiet
owned
chmod 000 "$SKILL"
run_hook "$TMP/bin" "$healthy" quiet
absent
chmod 644 "$SKILL"
for missing in glim jq timeout; do
  run_hook "$TMP/bin" "$healthy" quiet
  owned
  run_hook "$TMP/no-$missing" "$healthy" quiet
  absent
done
run_hook "$TMP/bin" "$healthy" quiet
owned
run_hook "$TMP/bin" "$healthy" quiet /usr/bin/env GLIM_EXIT=1
absent
for response in \
  '{"ok":false,"result":{"ok":true}}' \
  '{"ok":true,"result":{"ok":false}}' \
  '{"ok":true}' \
  'not-json' \
  '   ' \
  ''; do
  run_hook "$TMP/bin" "$healthy" quiet
  owned
  run_hook "$TMP/bin" "$response" quiet
  absent
done
run_hook "$TMP/bin" "$healthy" quiet
owned
run_hook "$TMP/bin" "$healthy" quiet /usr/bin/env GLIM_DELAY=4
absent
run_hook "$TMP/bin" "$healthy" quiet
owned

# A dangling link with the expected target still belongs to the hook.
rm -r "$SOURCE"
run_hook "$TMP/bin" "$healthy" quiet
absent
mkdir -p "$SOURCE"
printf 'Glimse instructions\n' >"$SKILL"

# Neither health state may overwrite or remove user-owned paths.
for kind in file directory foreign dangling; do
  case "$kind" in
    file) printf 'user skill\n' >"$LINK" ;;
    directory) mkdir "$LINK"; printf 'user skill\n' >"$LINK/keep" ;;
    foreign) ln -s "$TMP/foreign" "$LINK"; printf 'user skill\n' >"$TMP/foreign" ;;
    dangling) ln -s "$TMP/missing" "$LINK" ;;
  esac
  run_hook "$TMP/bin" "$healthy" conflict
  run_hook "$TMP/no-jq" "$healthy" conflict
  case "$kind" in
    file) [[ "$(<"$LINK")" == 'user skill' ]] || fail 'user file changed'; rm "$LINK" ;;
    directory) [[ "$(<"$LINK/keep")" == 'user skill' ]] || fail 'user directory changed'; rm -r "$LINK" ;;
    foreign) [[ "$(readlink "$LINK")" == "$TMP/foreign" ]] || fail 'foreign link changed'; rm "$LINK" ;;
    dangling) [[ -L "$LINK" && "$(readlink "$LINK")" == "$TMP/missing" ]] || fail 'dangling foreign link changed'; rm "$LINK" ;;
  esac
done

printf 'Claude Glim skill hook passed\n'
