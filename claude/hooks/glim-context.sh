#!/usr/bin/env bash

source="$HOME/.pi/agent/git/github.com/ryan-ressmeyer/glim/integrations/generic-skill/glim"
link="$HOME/.claude/skills/glim"
healthy=false
if [[ -r "$source/SKILL.md" ]] && command -v glim >/dev/null 2>&1 &&
   command -v jq >/dev/null 2>&1 && command -v timeout >/dev/null 2>&1; then
  status="$(timeout 2s glim status 2>/dev/null)" &&
    [[ -n "${status//[[:space:]]/}" ]] &&
    jq -e '.ok == true and .result.ok == true' >/dev/null 2>&1 <<<"$status" && healthy=true
fi

if [[ -L "$link" && "$(readlink "$link")" == "$source" ]]; then
  if [[ "$healthy" == false ]]; then
    rm -- "$link" || printf 'Could not remove Glim skill link: %s\n' "$link" >&2
  fi
elif [[ -e "$link" || -L "$link" ]]; then
  printf 'Glim skill path conflict: %s\n' "$link" >&2
elif [[ "$healthy" == true ]]; then
  if ! mkdir -p -- "$HOME/.claude/skills" || ! ln -s -- "$source" "$link"; then
    printf 'Could not create Glim skill link: %s\n' "$link" >&2
  fi
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"SessionStart","reloadSkills":true}}'
