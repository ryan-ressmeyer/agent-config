#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="$ROOT/pi/agents/investigator.md"
DELEGATE="$ROOT/pi/agents/delegate.md"

[[ -f "$AGENT" ]] || {
  printf 'missing investigator agent: %s\n' "$AGENT" >&2
  exit 1
}

[[ ! -e "$DELEGATE" ]] || {
  printf 'obsolete delegate agent must be replaced: %s\n' "$DELEGATE" >&2
  exit 1
}

grep -Eq '^description: .+' "$AGENT" || {
  printf 'investigator agent needs a routing description for ambient discovery\n' >&2
  exit 1
}

grep -Fxq 'model: openai-codex/gpt-6-astra' "$AGENT" || {
  printf 'investigator agent must default to GPT-6 Astra\n' >&2
  exit 1
}

grep -Fxq 'allow-model-override: false' "$AGENT" || {
  printf 'investigator agent must remain pinned to GPT-6 Astra\n' >&2
  exit 1
}

grep -Fxq 'spawning: false' "$AGENT" || {
  printf 'investigator agent must not spawn subagents\n' >&2
  exit 1
}

printf 'investigator agent contract passed\n'
