# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal agent configuration for [pi](https://github.com/badlogic/pi-mono) and Claude Code. Single source of truth for skills, settings fragments, per-machine context, and pi-only resources (extensions, prompts, themes, and extension configuration).

After any change, re-run `./install.sh` to regenerate context files and re-merge settings. The script is idempotent.

## Install on a new machine

```bash
git clone git@github.com:ryan-ressmeyer/agent-config.git ~/code/agent-config
cd ~/code/agent-config
./install.sh
```

## Key architecture

`install.sh` does six things:

1. **Creates `machines/<hostname>/`** from `machines/default/` if it doesn't exist yet.
2. **Symlinks** each categorized skill into the flat `~/.claude/skills/` and `~/.agents/skills/` namespaces; pi-only dirs → `~/.pi/agent/`.
3. **Installs extension configuration**, including the managed Blackhole preset and the shared Ponytail default-mode config under the XDG config directory.
4. **Generates context files** (not symlinks): concatenates `machines/<hostname>/context.md` + `shared/AGENTS.md` into `~/.claude/CLAUDE.md` and `~/.pi/agent/AGENTS.md`. Machine context goes first.
5. **Merges settings fragments** idempotently via `scripts/merge-json.py`: dict keys override, list items union. Order: `pi/settings.fragment.json` → `machines/<hostname>/settings.fragment.json` → `~/.pi/agent/settings.json`; `claude/settings.fragment.json` → `~/.claude/settings.json`.
6. **Skips OpenRouter key setup in headless runs**, then installs the pre-commit hook (`scripts/check-no-secrets.sh`) that blocks `auth.json`, `.env`, and staged API key patterns.

## Adding skills

Add `skills/<category>/<name>/SKILL.md`, then run `./install.sh` to create its individual links.

Skills require YAML frontmatter with `name` (lowercase letters, numbers, and hyphens) and `description` (≤1024 characters, starts with "Use when…", third-person, retrieval or invocation triggers only — never a workflow summary). User-invoked workflows may also set `disable-model-invocation: true`; reference skills must remain model-invoked so agents can retrieve them when relevant. See `skills/agent-workflows/writing-skills/SKILL.md` for the evaluation-driven authoring process.

Optional subdirectories per skill: `references/`, `assets/`, `source/`.

## Per-machine customization

- Edit `machines/<hostname>/context.md` for machine-specific facts (paths, hardware, use cases).
- Edit `machines/<hostname>/settings.fragment.json` for per-machine settings overrides (model, permissions). Fragment values win over base.
- Re-run `./install.sh` after editing machine files.

## scripts/merge-json.py

Merges a JSON fragment into a target file. Dicts merge recursively (fragment wins on conflicts), lists union (fragment items appended if absent), scalars override. Run with `uv run scripts/merge-json.py <fragment> <target>`.

In a list, a string prefixed with `!` removes its match from the merged result instead of being appended — this is how a per-machine fragment opts out of something the base fragment adds (see `machines/solo/settings.fragment.json`). Because the merge target is the live settings file, an exclusion also strips an entry a previous install already wrote. Items apply in order, so `["a", "!a"]` within one fragment nets to absent. Write `\!` for a literal `!`.

Tests: `tests/merge-json-exclusions.sh` and `tests/install-nested-skills.sh`. Both are self-contained — run them directly.

## Secrets

Never commit `auth.json`, `.env`, or API keys. The pre-commit hook blocks them automatically. OpenRouter keys live in `~/.pi/agent/auth.json` (mode 600), written by `install.sh` on first run.
