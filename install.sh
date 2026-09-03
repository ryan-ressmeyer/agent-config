#!/usr/bin/env bash
# agent-config installer — idempotent.
# Wires skills, agents, extensions, prompts, themes, context files, and settings
# into pi (~/.pi/agent/), Claude Code (~/.claude/), and Codex (~/.codex/).
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || hostname)"
MACHINE_DIR="$REPO/machines/$HOSTNAME_SHORT"
DEFAULT_MACHINE_DIR="$REPO/machines/default"

PI_DIR="$HOME/.pi/agent"
CLAUDE_DIR="$HOME/.claude"
CODEX_DIR="$HOME/.codex"
AGENTS_DIR="$HOME/.agents"

MERGE="$REPO/scripts/merge-json.py"

# --- helpers ---

info()  { printf '\033[1;34m•\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m!\033[0m %s\n' "$*" >&2; }
error() { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# symlink <source> <target>
# - source must exist
# - if target is correct symlink: skip
# - if target is other symlink: replace
# - if target is real file/dir: abort (user must handle)
symlink() {
  local src="$1"
  local target="$2"

  [[ -e "$src" ]] || error "source does not exist: $src"
  mkdir -p "$(dirname "$target")"

  if [[ -L "$target" ]]; then
    local current
    current="$(readlink "$target")"
    if [[ "$current" == "$src" ]]; then
      ok "symlink OK: $target → $src"
      return 0
    fi
    warn "replacing stale symlink: $target (was → $current)"
    rm "$target"
  elif [[ -e "$target" ]]; then
    error "target exists and is not a symlink: $target (move or remove it, then re-run)"
  fi

  ln -s "$src" "$target"
  ok "linked: $target → $src"
}

# --- step 1: machine context ---

ensure_machine_dir() {
  if [[ ! -d "$MACHINE_DIR" ]]; then
    info "no machine directory for '$HOSTNAME_SHORT' — creating from default"
    cp -r "$DEFAULT_MACHINE_DIR" "$MACHINE_DIR"
    warn "edit $MACHINE_DIR/context.md with machine-specific details, then commit it"
  else
    ok "machine directory exists: $MACHINE_DIR"
  fi
}

# --- step 2: symlinks ---

install_skill_links() {
  local -a skill_dirs
  mapfile -t skill_dirs < <(
    find "$REPO/skills" -mindepth 3 -maxdepth 3 -type f -name SKILL.md -printf '%h\n' | sort
  )
  [[ ${#skill_dirs[@]} -gt 0 ]] || error "no skills found under $REPO/skills/<category>/<name>"

  local -A names=()
  local skill_dir skill_name
  for skill_dir in "${skill_dirs[@]}"; do
    skill_name="$(basename "$skill_dir")"
    [[ -z "${names[$skill_name]:-}" ]] || \
      error "duplicate skill name '$skill_name': ${names[$skill_name]} and $skill_dir"
    names[$skill_name]="$skill_dir"
  done

  local target_root current target link_name
  for target_root in "$CLAUDE_DIR/skills" "$AGENTS_DIR/skills"; do
    if [[ -L "$target_root" ]]; then
      current="$(readlink "$target_root")"
      warn "replacing legacy skill-directory symlink: $target_root (was → $current)"
      rm "$target_root"
    elif [[ -e "$target_root" && ! -d "$target_root" ]]; then
      error "skill target exists and is not a directory: $target_root"
    fi
    mkdir -p "$target_root"

    for target in "$target_root"/*; do
      [[ -L "$target" ]] || continue
      current="$(readlink "$target")"
      link_name="$(basename "$target")"
      if [[ "$current" == "$REPO/skills/"* && -z "${names[$link_name]:-}" ]]; then
        warn "removing stale managed skill symlink: $target (was → $current)"
        rm "$target"
      fi
    done

    for skill_dir in "${skill_dirs[@]}"; do
      skill_name="$(basename "$skill_dir")"
      symlink "$skill_dir" "$target_root/$skill_name"
    done
  done
}

install_symlinks() {
  info "installing symlinks"
  # Categorized in the repository, flattened for discovery by both tools.
  install_skill_links

  # pi-only resources
  symlink "$REPO/pi/agents"     "$PI_DIR/agents"
  symlink "$REPO/pi/extensions" "$PI_DIR/extensions"
  symlink "$REPO/pi/prompts"    "$PI_DIR/prompts"
  symlink "$REPO/pi/themes"     "$PI_DIR/themes"
}

# --- step 3: managed pi config files ---

install_pi_configs() {
  info "installing pi config files"
  local blackhole_source="$REPO/pi/pi-blackhole/pi-blackhole-config.json"
  local blackhole_target="$PI_DIR/pi-blackhole/pi-blackhole-config.json"

  mkdir -p "$(dirname "$blackhole_target")"
  install -m 0644 "$blackhole_source" "$blackhole_target"
  ok "wrote $blackhole_target"
}

install_ponytail_config() {
  info "installing Ponytail config"
  local config_root="${XDG_CONFIG_HOME:-$HOME/.config}"
  local source="$REPO/ponytail/config.json"
  local target="$config_root/ponytail/config.json"

  mkdir -p "$(dirname "$target")"
  install -m 0644 "$source" "$target"
  ok "wrote $target"
}

# --- step 4: generated context files ---
# AGENTS.md / CLAUDE.md are generated, not symlinked, so per-machine content
# stays per-machine.

generate_context_files() {
  info "generating context files"
  local combined
  combined="$(mktemp)"
  trap "rm -f '$combined'" RETURN

  # Machine context first (background / environmental facts), then shared
  # (default posture and skill guidance — the part most relevant to current
  # work should sit closest to the conversation).
  if [[ -f "$MACHINE_DIR/context.md" ]]; then
    cat "$MACHINE_DIR/context.md" > "$combined"
    printf '\n\n' >> "$combined"
  fi
  cat "$REPO/shared/AGENTS.md" >> "$combined"

  mkdir -p "$PI_DIR" "$CLAUDE_DIR" "$CODEX_DIR"
  install -m 0644 "$combined" "$PI_DIR/AGENTS.md"
  install -m 0644 "$combined" "$CLAUDE_DIR/CLAUDE.md"
  install -m 0644 "$combined" "$CODEX_DIR/AGENTS.md"
  ok "wrote $PI_DIR/AGENTS.md"
  ok "wrote $CLAUDE_DIR/CLAUDE.md"
  ok "wrote $CODEX_DIR/AGENTS.md"
}

# --- step 5: settings merges ---

merge_settings() {
  info "merging settings fragments"

  # Pi: base fragment, then per-machine (if non-empty)
  "$MERGE" "$REPO/pi/settings.fragment.json"                 "$PI_DIR/settings.json"
  if [[ -f "$MACHINE_DIR/settings.fragment.json" ]]; then
    "$MERGE" "$MACHINE_DIR/settings.fragment.json"           "$PI_DIR/settings.json"
  fi

  "$MERGE" "$REPO/pi/keybindings.fragment.json"              "$PI_DIR/keybindings.json"

  # Claude
  "$MERGE" "$REPO/claude/settings.fragment.json"             "$CLAUDE_DIR/settings.json"
}

# --- step 6: OpenRouter key ---

ensure_openrouter_key() {
  info "checking OpenRouter API key"
  local auth="$PI_DIR/auth.json"
  mkdir -p "$PI_DIR"

  local has_key="no"
  if [[ -f "$auth" ]] && python3 -c "
import json, sys
try:
    with open('$auth') as f:
        data = json.load(f)
    sys.exit(0 if data.get('openrouter', {}).get('key') else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
    has_key="yes"
  fi

  if [[ "$has_key" == "yes" ]]; then
    ok "OpenRouter key already present in $auth"
    return 0
  fi

  if [[ ! -t 0 ]]; then
    warn "no interactive input; skipping OpenRouter key setup"
    return 0
  fi

  echo ""
  read -r -p "Enter OpenRouter API key (or leave blank to skip): " key
  if [[ -z "$key" ]]; then
    warn "skipped OpenRouter key setup — pi may not authenticate"
    return 0
  fi

  python3 - "$auth" "$key" <<'PY'
import json, os, sys
path, key = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        data = {}
data.setdefault("openrouter", {})
data["openrouter"]["type"] = "api_key"
data["openrouter"]["key"] = key
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
os.chmod(path, 0o600)
PY
  ok "wrote OpenRouter key to $auth (mode 600)"
}

# --- step 7: pre-commit hook ---

install_precommit_hook() {
  info "installing pre-commit hook"
  local hook_src="$REPO/scripts/check-no-secrets.sh"
  local hook_dst="$REPO/.git/hooks/pre-commit"

  if [[ ! -d "$REPO/.git" ]]; then
    warn "not a git repo; skipping pre-commit hook"
    return 0
  fi

  if [[ -L "$hook_dst" ]]; then
    local current
    current="$(readlink "$hook_dst")"
    if [[ "$current" == "$hook_src" ]]; then
      ok "pre-commit hook OK"
      return 0
    fi
    rm "$hook_dst"
  elif [[ -e "$hook_dst" ]]; then
    warn "existing non-symlink pre-commit hook at $hook_dst; leaving it alone"
    return 0
  fi

  ln -s "$hook_src" "$hook_dst"
  ok "linked pre-commit hook: $hook_dst"
}

# --- main ---

main() {
  info "installing agent-config from $REPO"
  info "hostname: $HOSTNAME_SHORT"
  echo ""

  ensure_machine_dir
  install_symlinks
  install_pi_configs
  install_ponytail_config
  generate_context_files
  merge_settings
  ensure_openrouter_key
  install_precommit_hook

  echo ""
  ok "install complete"
}

main "$@"
