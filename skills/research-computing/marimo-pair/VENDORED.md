# Vendored skill

This directory is vendored (copied) from an upstream project, not authored here.

- **Source:** https://github.com/marimo-team/marimo-pair
- **Commit:** `5368e127e736881fedd6bd7db315f6f974290230`
- **License:** Apache-2.0 (see `LICENSE`)

## Why vendored, not plugin-installed

This repo is the single source of truth for skills, symlinked to both
`~/.claude/skills` (Claude Code) and `~/.agents/skills` (pi). Vendoring lets
both agents pick it up through the existing symlinks. The trade-off is no
auto-update.

## Updating

Re-copy `skills/research-computing/marimo-pair/` and `LICENSE` from a fresh clone of the upstream
repo and bump the commit above. `marimo-pair`'s commit API `cm`
(`marimo._code_mode`) is private and unstable across marimo versions, so pin
the marimo version in research workspaces and re-check this skill after marimo
upgrades. Do not hand-edit the vendored files — local edits are lost on update;
put local policy in the `exploratory-notebook` skill instead.
