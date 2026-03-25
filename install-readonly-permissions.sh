#!/usr/bin/env bash
# install-readonly-permissions.sh
# Adds read-only tool and bash command permissions to ~/.claude/settings.json
# Safe to run multiple times — merges with existing settings without duplicates.

set -euo pipefail

SETTINGS_FILE="${HOME}/.claude/settings.json"

# All read-only permissions to add
READONLY_PERMISSIONS=(
  # Dedicated read-only tools
  "Read"
  "Glob"
  "Grep"
  "WebFetch"
  "WebSearch"
  "LSP"

  # Git read-only commands
  "Bash(git status *)"
  "Bash(git log *)"
  "Bash(git diff *)"
  "Bash(git show *)"
  "Bash(git blame *)"
  "Bash(git branch *)"
  "Bash(git remote *)"
  "Bash(git tag *)"
  "Bash(git stash list *)"
  "Bash(git rev-parse *)"

  # Filesystem read-only commands
  "Bash(ls *)"
  "Bash(pwd)"
  "Bash(tree *)"
  "Bash(wc *)"
  "Bash(file *)"
  "Bash(which *)"
  "Bash(type *)"
  "Bash(du *)"
  "Bash(df *)"
  "Bash(stat *)"

  # Version / environment info
  "Bash(uv --version)"
  "Bash(node --version)"
  "Bash(python --version)"
  "Bash(python3 --version)"
  "Bash(gh --version)"
  "Bash(printenv *)"
  "Bash(env)"
)

# Ensure ~/.claude directory exists
mkdir -p "$(dirname "$SETTINGS_FILE")"

# Create settings file if it doesn't exist
if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo '{}' > "$SETTINGS_FILE"
fi

# Use Python (via uv if available, else python3) to merge permissions
PYTHON_CMD="python3"
if command -v uv &>/dev/null; then
  PYTHON_CMD="uv run python3"
fi

# Build JSON array of permissions to add
PERMS_JSON=$(printf '%s\n' "${READONLY_PERMISSIONS[@]}" | $PYTHON_CMD -c "
import sys, json
perms = [line.strip() for line in sys.stdin if line.strip()]
print(json.dumps(perms))
")

# Merge into settings.json
$PYTHON_CMD -c "
import json, sys

settings_file = '${SETTINGS_FILE}'
new_perms = json.loads('${PERMS_JSON}')

with open(settings_file, 'r') as f:
    settings = json.load(f)

# Ensure permissions.allow exists
settings.setdefault('permissions', {})
settings['permissions'].setdefault('allow', [])

# Add only permissions not already present
existing = set(settings['permissions']['allow'])
added = []
for perm in new_perms:
    if perm not in existing:
        settings['permissions']['allow'].append(perm)
        added.append(perm)

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')

if added:
    print(f'Added {len(added)} read-only permissions to {settings_file}:')
    for p in added:
        print(f'  + {p}')
else:
    print(f'All read-only permissions already present in {settings_file}.')
"
