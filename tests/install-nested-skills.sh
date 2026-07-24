#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/agent-config"
HOME_DIR="$TMP/home"
mkdir -p "$REPO" "$HOME_DIR/.claude" "$HOME_DIR/.agents"
cp -a \
  "$ROOT/install.sh" \
  "$ROOT/scripts" \
  "$ROOT/pi" \
  "$ROOT/claude" \
  "$ROOT/shared" \
  "$ROOT/machines" \
  "$ROOT/skills" \
  "$REPO/"

# Model the desired source layout independently of the production repository.
mkdir -p "$REPO/skills/test-category"
for skill in "$REPO"/skills/*; do
  [[ -f "$skill/SKILL.md" ]] || continue
  mv "$skill" "$REPO/skills/test-category/"
done

# Model an existing installation made by the legacy whole-directory installer.
ln -s "$REPO/skills" "$HOME_DIR/.claude/skills"
ln -s "$REPO/skills" "$HOME_DIR/.agents/skills"

printf '\n' | HOME="$HOME_DIR" "$REPO/install.sh" >/dev/null

# Model links left behind after a managed skill is deleted, plus an unrelated
# user-managed link that the installer must preserve.
mkdir -p "$TMP/custom-skill"
for target_root in "$HOME_DIR/.claude/skills" "$HOME_DIR/.agents/skills"; do
  ln -s "$REPO/skills/removed-category/removed-skill" "$target_root/removed-skill"
  ln -s "$TMP/custom-skill" "$target_root/custom-skill"
done

printf '\n' | HOME="$HOME_DIR" "$REPO/install.sh" >/dev/null

for target_root in "$HOME_DIR/.claude/skills" "$HOME_DIR/.agents/skills"; do
  [[ ! -L "$target_root/removed-skill" ]] || {
    printf 'stale managed skill link was not removed: %s\n' "$target_root/removed-skill" >&2
    exit 1
  }
  [[ -L "$target_root/custom-skill" ]] || {
    printf 'unrelated skill link was removed: %s\n' "$target_root/custom-skill" >&2
    exit 1
  }

  [[ -d "$target_root" && ! -L "$target_root" ]] || {
    printf 'expected a real skill directory: %s\n' "$target_root" >&2
    exit 1
  }

  while IFS= read -r skill_file; do
    source_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$source_dir")"
    target="$target_root/$skill_name"
    [[ -L "$target" ]] || {
      printf 'expected skill symlink: %s\n' "$target" >&2
      exit 1
    }
    [[ "$(readlink "$target")" == "$source_dir" ]] || {
      printf 'wrong skill target: %s -> %s\n' "$target" "$(readlink "$target")" >&2
      exit 1
    }
  done < <(find "$REPO/skills" -mindepth 3 -maxdepth 3 -type f -name SKILL.md | sort)
done

printf 'nested skill installation passed\n'
