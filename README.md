# agent-config

Personal coding-agent configuration for [pi](https://github.com/badlogic/pi-mono) and [Claude Code](https://claude.ai/code).

Single source of truth for:
- **Skills** (cross-tool, symlinked into both agents)
- **Pi extensions, prompts, themes** (pi-only, symlinked into `~/.pi/agent/`)
- **Global context files** (generated `AGENTS.md` / `CLAUDE.md`)
- **Settings fragments** (idempotently merged into each tool's settings.json)
- **Per-machine overrides** (hostname-keyed)

## Install

On a fresh machine:

```bash
git clone git@github.com:ryan-ressmeyer/agent-config.git ~/code/agent-config
cd ~/code/agent-config
./install.sh
```

The script is idempotent — re-run it any time after pulling changes.

## Layout

```
agent-config/
├── install.sh                  # entry point
├── skills/                     # universal; symlinked to ~/.agents/skills and ~/.claude/skills
├── pi/
│   ├── extensions/             # pi-only TS extensions
│   ├── prompts/                # pi-only /slash templates
│   ├── themes/                 # pi-only themes
│   ├── settings.fragment.json  # merged into ~/.pi/agent/settings.json
│   └── keybindings.fragment.json
├── claude/
│   └── settings.fragment.json  # merged into ~/.claude/settings.json
├── shared/
│   └── AGENTS.md               # common context; prepended into both tools' context files
├── machines/
│   ├── default/                # template; copied to machines/<hostname>/ on first install
│   └── <hostname>/             # per-machine context + settings overrides
├── scripts/
│   ├── merge-json.py           # idempotent JSON fragment merger
│   ├── check-no-secrets.sh     # pre-commit hook
│   └── ...
└── docs/                       # design notes and historical plans
```

## What `install.sh` does

1. **Ensures a machine directory exists** for `$HOSTNAME` (copies from `machines/default/` if absent).
2. **Creates symlinks:**
   - `skills/` → `~/.claude/skills` and `~/.agents/skills`
   - `pi/{extensions,prompts,themes}/` → `~/.pi/agent/{extensions,prompts,themes}`
3. **Generates context files** (NOT symlinks): concatenates `machines/$HOSTNAME/context.md` + `shared/AGENTS.md` (machine first, shared second) into `~/.pi/agent/AGENTS.md` and `~/.claude/CLAUDE.md`.
4. **Merges settings fragments** idempotently:
   - `pi/settings.fragment.json` + `machines/$HOSTNAME/settings.fragment.json` → `~/.pi/agent/settings.json`
   - `pi/keybindings.fragment.json` → `~/.pi/agent/keybindings.json`
   - `claude/settings.fragment.json` → `~/.claude/settings.json`
5. **Prompts for the OpenRouter API key** if not already in `~/.pi/agent/auth.json`; writes it with mode 600.
6. **Installs the pre-commit hook** (`scripts/check-no-secrets.sh`) into this repo's `.git/hooks/`.

## Adding new skills, extensions, prompts, themes

Just drop them into the matching directory. The symlinks already resolve.

- New skill: `skills/<name>/SKILL.md` (+ optional `references/`, `assets/`, `scripts/`)
- New pi extension: `pi/extensions/<name>.ts` (or directory)
- New pi prompt: `pi/prompts/<name>.md`
- New pi theme: `pi/themes/<name>.ts`

No `install.sh` re-run needed unless you're adding a new symlinked directory.

## Per-machine customization

Edit `machines/<hostname>/context.md` with machine-specific info the agent should know automatically (paths, hardware, use cases).

For per-machine settings overrides (different model, thinking level, permissions), edit `machines/<hostname>/settings.fragment.json`. These merge on top of the base `pi/settings.fragment.json` with fragment values winning.

Re-run `install.sh` after editing machine files to regenerate context and re-merge settings.

## Secrets

- **Never** commit `auth.json`, `.env`, or API keys. `.gitignore` and the pre-commit hook both block them.
- OpenRouter keys live in `~/.pi/agent/auth.json` (mode 600) — populated by `install.sh` on first run.

## Skill index

See `skills/` — each subdirectory is an agent skill with a `SKILL.md`. Skills cover:

- **Literature & research:** `literature-review`, `paper-summarize`, `pdf-retrieve`, `citation-fetch`, `database-search`, `database-check`, `theme-synthesize`, `citation-management`
- **Writing:** `literature-writer`, `manuscript-planning`, `manuscript-review`, `manuscript-editing`, `reverse-outline`, `section-critique`, `critique-triage`, `copy-review`, `style-guide`, `presentation-planning`
- **Process & code:** `verification-before-completion`, `writing-skills`, `python-environment`, `uv-research-workspace`, `git-commits`, `systematic-debugging`, `test-driven-development`
- **Obsidian & web:** `obsidian-cli`, `obsidian-markdown`, `obsidian-bases`, `obsidian-literature-review`, `json-canvas`, `defuddle`

## Sources

- [obra/superpowers](https://github.com/obra/superpowers) — process skills
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — scientific skills (heavily reworked)
