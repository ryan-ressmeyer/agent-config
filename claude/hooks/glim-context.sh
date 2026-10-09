#!/usr/bin/env bash

skill="$HOME/.pi/agent/git/github.com/ryan-ressmeyer/glim/integrations/generic-skill/glim/SKILL.md"
[[ -r "$skill" ]] || exit 0
for tool in glim jq timeout; do
  command -v "$tool" >/dev/null 2>&1 || exit 0
done

status="$(timeout 2s glim status 2>/dev/null)" || exit 0
[[ -n "${status//[[:space:]]/}" ]] || exit 0
jq -e '.ok == true and .result.ok == true' >/dev/null 2>&1 <<<"$status" || exit 0

printf 'Glimse is available for publishing deliberate visual or inspectable artifacts. Before using it, read %s and follow its linked references. Do not publish routine diffs, logs, or status updates.\n' "$skill"
