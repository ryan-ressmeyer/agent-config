#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="$ROOT/pi/agents/scout.md"
[[ -f "$AGENT" ]] || { printf 'missing scout agent\n' >&2; exit 1; }

for field in \
  'name: scout' \
  'mode: background' \
  'auto-exit: true' \
  'async: true' \
  'session-mode: lineage-only' \
  'tools: read,grep,find,ls,ssh_inspect,caller_ping' \
  'extensions: git:github.com/DietrichGebert/ponytail@v4.9.0, ~/.pi/agent/extensions/ssh-inspect.ts' \
  'skills: none' \
  'spawning: false' \
  'model: openai-codex/gpt-6-luna' \
  'thinking: low' \
  'allow-model-override: false'; do
  grep -Fxq "$field" "$AGENT" || { printf 'scout missing %s\n' "$field" >&2; exit 1; }
done

! grep -q '^no-context-files: true' "$AGENT" || {
  printf 'scout must retain project context\n' >&2; exit 1;
}
grep -Eq '^description: .*([Ss]earch|[Mm]ap|[Ee]numerat)' "$AGENT" || {
  printf 'scout needs a discovery routing description\n' >&2; exit 1;
}
grep -Eq 'scope .*miss|miss.*scope' "$AGENT" || {
  printf 'scout must report scope on a miss\n' >&2; exit 1;
}
grep -Eq 'ambiguity .*parent|parent .*ambiguity' "$AGENT" || {
  printf 'scout must escalate ambiguity to parent\n' >&2; exit 1;
}

[[ -f "$ROOT/pi/extensions/ssh-inspect.ts" ]] || {
  printf 'scout remote inspection extension is missing\n' >&2; exit 1;
}
grep -q 'For remote discovery, use ssh_inspect' "$AGENT" || {
  printf 'scout must document remote discovery with ssh_inspect\n' >&2; exit 1;
}

printf 'scout agent contract passed\n'
