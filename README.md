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

The script is idempotent. Re-run it after pulling changes. When stdin is not interactive, installation skips OpenRouter key setup instead of prompting.

## Automatic updates in pi

The `agent-config-updater` extension checks `origin/main` in the background when pi starts. If the local checkout is clean and can be fast-forwarded, it offers to pull the changes, run `install.sh`, and reload pi's resources. If upstream changes exist but the checkout is dirty, diverged, detached, or on another branch, it warns without modifying the repository.

Run `/config-update` to check manually. The extension finds this repository through its installed extension path, so it does not depend on a fixed clone location.

## Layout

```
agent-config/
├── install.sh                  # entry point
├── skills/                     # categorized sources; individually linked into each agent
│   └── <category>/<name>/      # each skill contains SKILL.md and optional supporting files
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
   - Each `skills/<category>/<name>/` → `~/.claude/skills/<name>` and `~/.agents/skills/<name>`
   - `pi/{extensions,prompts,themes}/` → `~/.pi/agent/{extensions,prompts,themes}`
3. **Generates context files** (NOT symlinks): concatenates `machines/$HOSTNAME/context.md` + `shared/AGENTS.md` (machine first, shared second) into `~/.pi/agent/AGENTS.md` and `~/.claude/CLAUDE.md`.
4. **Merges settings fragments** idempotently:
   - `pi/settings.fragment.json` + `machines/$HOSTNAME/settings.fragment.json` → `~/.pi/agent/settings.json`
   - `pi/keybindings.fragment.json` → `~/.pi/agent/keybindings.json`
   - `claude/settings.fragment.json` → `~/.claude/settings.json`
5. **Prompts for the OpenRouter API key** during interactive installation if it is absent from `~/.pi/agent/auth.json`; headless runs skip this step.
6. **Installs the pre-commit hook** (`scripts/check-no-secrets.sh`) into this repo's `.git/hooks/`.

## Adding new skills, extensions, prompts, themes

Add resources to the matching directory.

- New skill: `skills/<category>/<name>/SKILL.md` (+ optional `references/`, `assets/`, `scripts/`)
- New pi extension: `pi/extensions/<name>.ts` (or directory)
- New pi prompt: `pi/prompts/<name>.md`
- New pi theme: `pi/themes/<name>.ts`

Re-run `./install.sh` after adding a skill so its individual links are created. Other resources appear through their existing directory links.

## Per-machine customization

Edit `machines/<hostname>/context.md` with machine-specific info the agent should know automatically (paths, hardware, use cases).

For per-machine settings overrides (different model, thinking level, permissions), edit `machines/<hostname>/settings.fragment.json`. These merge on top of the base `pi/settings.fragment.json` with fragment values winning.

Lists union rather than override, so a machine fragment can add to a list but not replace it. To drop something the base fragment adds, prefix it with `!`:

```json
{
  "packages": [
    "!npm:pi-smart-fetch"
  ]
}
```

This is how `solo` opts out of `pi-smart-fetch`, whose native `wreq-js` module needs glibc 2.34 while Ubuntu 20.04 ships 2.31. Every other machine still gets it.

Re-run `install.sh` after editing machine files to regenerate context and re-merge settings.

## Secrets

- **Never** commit `auth.json`, `.env`, or API keys. `.gitignore` and the pre-commit hook both block them.
- OpenRouter keys live in `~/.pi/agent/auth.json` (mode 600) — populated by `install.sh` on first run.

## Skill categories

- `agent-workflows/` — reusable agent process skills
- `communication/` — manuscripts, reviews, presentations, and style
- `infrastructure/` — machine and server operations
- `knowledge/` — literature discovery, paper summaries, and thematic synthesis
- `research-computing/` — uv workspaces and marimo notebooks
- `software/` — Python environments, Git, testing, debugging, and verification

## Sources

- [obra/superpowers](https://github.com/obra/superpowers) — process skills
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — scientific skills (heavily reworked)
