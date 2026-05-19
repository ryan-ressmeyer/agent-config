# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal agent configuration for [pi](https://github.com/badlogic/pi-mono) and Claude Code. Single source of truth for skills, settings fragments, per-machine context, and pi-only resources (extensions, prompts, themes).

After any change, re-run `./install.sh` to regenerate context files and re-merge settings. The script is idempotent.

## Install on a new machine

```bash
git clone git@github.com:ryan-ressmeyer/agent-config.git ~/code/agent-config
cd ~/code/agent-config
./install.sh
```

## Key architecture

`install.sh` does five things:

1. **Creates `machines/<hostname>/`** from `machines/default/` if it doesn't exist yet.
2. **Symlinks** `skills/` → `~/.claude/skills` and `~/.agents/skills`; pi-only dirs → `~/.pi/agent/`.
3. **Generates context files** (not symlinks): concatenates `machines/<hostname>/context.md` + `shared/AGENTS.md` into `~/.claude/CLAUDE.md` and `~/.pi/agent/AGENTS.md`. Machine context goes first.
4. **Merges settings fragments** idempotently via `scripts/merge-json.py`: dict keys override, list items union. Order: `pi/settings.fragment.json` → `machines/<hostname>/settings.fragment.json` → `~/.pi/agent/settings.json`; `claude/settings.fragment.json` → `~/.claude/settings.json`.
5. **Installs the pre-commit hook** (`scripts/check-no-secrets.sh`) that blocks `auth.json`, `.env`, and staged API key patterns.

## Adding skills

Drop `skills/<name>/SKILL.md` into the skills directory — the symlink already resolves. No `install.sh` re-run needed.

Skills require YAML frontmatter with only `name` (letters, numbers, hyphens) and `description` (≤1024 chars total, starts with "Use when…", third-person, triggering conditions only — never workflow summary). See `skills/writing-skills/SKILL.md` for the full authoring process (TDD-based: write a failing pressure test first, then write the skill, then close loopholes).

Optional subdirectories per skill: `references/`, `assets/`, `source/`.

## Per-machine customization

- Edit `machines/<hostname>/context.md` for machine-specific facts (paths, hardware, use cases).
- Edit `machines/<hostname>/settings.fragment.json` for per-machine settings overrides (model, permissions). Fragment values win over base.
- Re-run `./install.sh` after editing machine files.

## scripts/merge-json.py

Merges a JSON fragment into a target file. Dicts merge recursively (fragment wins on conflicts), lists union (fragment items appended if absent), scalars override. Run with `uv run scripts/merge-json.py <fragment> <target>`.

## Secrets

Never commit `auth.json`, `.env`, or API keys. The pre-commit hook blocks them automatically. OpenRouter keys live in `~/.pi/agent/auth.json` (mode 600), written by `install.sh` on first run.
