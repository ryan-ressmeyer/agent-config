#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="$ROOT/pi/agents/qlmri.md"

[[ -f "$AGENT" ]] || {
  printf 'missing QLMRI agent: %s\n' "$AGENT" >&2
  exit 1
}

grep -Eq '^description: .+' "$AGENT" || {
  printf 'QLMRI agent needs a routing description for ambient discovery\n' >&2
  exit 1
}

grep -Fxq 'model: openai-codex/gpt-5.6-terra' "$AGENT" || {
  printf 'QLMRI agent must default to GPT-5.6 Terra\n' >&2
  exit 1
}

grep -Fxq 'allow-model-override: false' "$AGENT" || {
  printf 'QLMRI agent must remain pinned to GPT-5.6 Terra\n' >&2
  exit 1
}

grep -Fxq 'context-warn-threshold: 80%' "$AGENT" || {
  printf 'QLMRI agent must preserve room to report before long-paper context compaction\n' >&2
  exit 1
}

grep -Fq "carries the user's approval for that exact write" "$AGENT" || {
  printf 'QLMRI agent must inherit approval for its delegated scratchpad write\n' >&2
  exit 1
}

for skill in ansa-reference paper-summarize scientific-claims-reference; do
  grep -Fq "\`$skill\`" "$AGENT" || {
    printf 'QLMRI agent is missing required skill: %s\n' "$skill" >&2
    exit 1
  }
done

printf 'QLMRI agent contract passed\n'
