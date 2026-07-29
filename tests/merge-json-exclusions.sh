#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MERGE="$ROOT/scripts/merge-json.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

# Merge fragments into a target in order, then print a compact JSON slice of the
# result. Usage: merged <python-expr over d> <target-json> <fragment-json>...
merged() {
  local expr="$1" target="$TMP/target.json"
  printf '%s' "$2" >"$target"
  shift 2
  local i=0
  for fragment in "$@"; do
    i=$((i + 1))
    printf '%s' "$fragment" >"$TMP/fragment-$i.json"
    "$MERGE" "$TMP/fragment-$i.json" "$target" >/dev/null
  done
  uv run --quiet python -c "
import json, sys
d = json.load(sys.stdin)
print(json.dumps($expr, separators=(',', ':')))
" <"$target"
}

# A bang-prefixed item removes its match, and the marker itself is never added.
result="$(merged 'd["packages"]' '{"packages": ["a", "b", "c"]}' '{"packages": ["!b"]}')"
[[ "$result" == '["a","c"]' ]] ||
  fail "exclusion did not remove the item: $result"

# Additions and exclusions coexist in one fragment.
result="$(merged 'd["packages"]' '{"packages": ["a", "b"]}' '{"packages": ["!a", "d"]}')"
[[ "$result" == '["b","d"]' ]] ||
  fail "mixed add/exclude fragment wrong: $result"

# Excluding an absent item is a no-op, not an error or a stray marker.
result="$(merged 'd["packages"]' '{"packages": ["a"]}' '{"packages": ["!zzz"]}')"
[[ "$result" == '["a"]' ]] ||
  fail "excluding an absent item changed the list: $result"

# A backslash escape yields a literal bang-prefixed value.
result="$(merged 'd["packages"]' '{"packages": []}' '{"packages": ["\\!literal"]}')"
[[ "$result" == '["!literal"]' ]] ||
  fail "escaped bang did not become a literal: $result"

# ...and that literal is itself removable.
result="$(merged 'd["packages"]' '{"packages": ["!literal"]}' '{"packages": ["!\\!literal"]}')"
[[ "$result" == '[]' ]] ||
  fail "could not exclude a literal bang value: $result"

# The install order (base adds, machine excludes) is stable across repeated runs.
result="$(merged 'd["packages"]' '{}' \
  '{"packages": ["keep", "drop"]}' '{"packages": ["!drop"]}' \
  '{"packages": ["keep", "drop"]}' '{"packages": ["!drop"]}')"
[[ "$result" == '["keep"]' ]] ||
  fail "repeated base+machine merge was not idempotent: $result"

# Exclusions reach lists nested inside dicts.
result="$(merged 'd["permissions"]["allow"]' \
  '{"permissions": {"allow": ["Bash(ls:*)", "Bash(rm:*)"]}}' \
  '{"permissions": {"allow": ["!Bash(rm:*)"]}}')"
[[ "$result" == '["Bash(ls:*)"]' ]] ||
  fail "exclusion did not apply to a nested list: $result"

# Non-string list items are untouched by the marker logic.
result="$(merged 'd["items"]' '{"items": [1, {"k": "v"}]}' '{"items": [2]}')"
[[ "$result" == '[1,{"k":"v"},2]' ]] ||
  fail "non-string list items were mangled: $result"

printf 'merge-json exclusions passed\n'
