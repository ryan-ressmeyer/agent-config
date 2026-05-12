---
name: ansa-literature-review
description: Use when building or expanding the literature knowledge graph, adding papers (DOI/PMID/arXiv/PDF), asking "what papers do I have on X", searching the database, finding related work, summarizing a paper, or synthesizing themes across papers. Orchestrates the ansa CLI/HTTP surface and delegates to paper-summarize and theme-synthesize.
---

# ansa Literature Review

## Overview

Interactive orchestrator for the ansa knowledge graph. The user drives the pace — the agent routes work to `ansa` CLI commands (which hit the daemon over HTTP) and delegates structured tasks to sub-skills.

**This is not automation.** The user reads each paper and decides what gets added, summarized, or synthesized. The agent handles metadata, search, and the mechanical edges of "where does this fit."

## Remote

Default remote on totoro is `kamaji` (`http://kamaji:7327`), pre-configured in `~/.config/ansa/remotes.yaml`. All commands below run unmodified — `ansa` resolves the remote from config. To target a different remote, pass `--remote NAME` or set `ANSA_REMOTE`.

If the remote is unreachable (`ansa node ls --type paper --limit 1` errors), stop and tell the user — `pdf-retrieve`-style fallbacks don't matter if the graph is offline.

## Session start

When a session opens, get oriented in one cheap call:

```bash
ansa node ls --type paper --limit 1                  # confirm remote is live
curl -s http://kamaji:7327/api/manifest | jq '{node_types: [.node_types[].name], plugins: [.plugins[].name]}'
```

That's enough to know what node types exist and which plugins are loaded. Don't print large dumps.

## Sub-skills

| Sub-skill | When the orchestrator delegates |
|---|---|
| `paper-summarize` | User says "summarize this paper", or a paper's scratchpad is empty and they want it filled |
| `theme-synthesize` | User wants a cross-paper synthesis on a topic, or asks "what's the theme across these N papers" |

Both sub-skills take a paper UUID (or a citekey/title fragment that resolves to one) and read/write through the ansa HTTP surface. The orchestrator's job is to get the user to the right sub-skill with the right UUIDs in hand.

## Modes

### Add a paper

Trigger: user supplies a DOI / arXiv ID / PMID / PDF and says "add this."

```bash
# By DOI
ansa paper import --doi 10.xxx/yyy

# By arXiv ID
ansa paper import --arxiv 2103.14030

# By local PDF
ansa paper import --pdf /path/to/paper.pdf

# Bulk from a .bib file
ansa paper import --bib refs.bib
```

`paper import` fetches metadata (Crossref / arXiv / Semantic Scholar) and, for arXiv, also downloads the PDF. **For Crossref DOIs the importer does not fetch the PDF** — only metadata. Auto-enrichment (OCR, embedding) runs synchronously after import unless disabled.

**When `--doi` succeeded but there's no PDF**, point the user at the DOI page:

> I have metadata for `<citekey>` but no PDF. Open https://doi.org/<doi>, download, and then run:
> `ansa paper import --pdf /path/to/<your-download>.pdf`
> The importer will deduplicate against the existing paper by DOI.

For paywalled cases the user can also try Unpaywall directly:

```bash
curl -s "https://api.unpaywall.org/v2/<doi>?email=ryan.ressmeyer@gmail.com" \
  | jq -r '.best_oa_location.url_for_pdf // empty'
```

If that returns a URL, `curl -L -o /tmp/<citekey>.pdf "<url>"`, validate with `head -c 4 /tmp/<citekey>.pdf` (must be `%PDF`), then `ansa paper import --pdf`. Never download from sci-hub or similar.

After import, surface the new paper's UUID and citekey to the user and ask whether to summarize it now (→ delegate to `paper-summarize`).

### Search / question mode

Trigger: "what do I have on X?", "find papers about Y", "is there a paper by Author on Z?"

```bash
# Full-text search across title, abstract, authors, notes, collections
ansa search "binocular rivalry temporal dynamics"

# Structured query
ansa query '{"type":"paper","where":{"year":{"ge":2020}},"order_by":"year","limit":20}'

# Semantic neighbors of a paper
ansa paper similar <UUID>
```

Read summaries (scratchpads) before answering — they're the user's own notes and outrank abstracts. Fetch a paper's scratchpad with `ansa paper scratchpad <UUID>`.

When the question implies papers outside the graph ("what does the field say about…?"), flag the gap explicitly: "I can answer from the N papers in the graph; if you want broader coverage, add specific papers and re-ask."

### Summarize a paper

Trigger: "summarize this paper", "write QLMRI for <X>", "what does this paper say?"

Resolve the input (UUID / citekey / title fragment) to a UUID, then delegate to `paper-summarize`. Confirm the resolved paper with the user when the input wasn't already a UUID — fuzzy matches happen.

### Synthesize a theme

Trigger: "synthesize across these papers", "what's the theme between A, B, C?", "make a theme document on Y."

Gather the candidate paper UUIDs (from a search, from a user list, or by walking a collection's members), then delegate to `theme-synthesize`. The theme is represented as a `collection` of `kind=theme` with member papers attached via `in_collection` edges; the synthesis itself is a `note` attached to that collection. The sub-skill handles the create-or-update logic.

### Browse existing themes / collections

```bash
ansa collection ls                                   # all collections, any kind
ansa collection ls --kind theme                      # just themes
ansa collection show <UUID>                          # name, description, member preview
ansa collection members <UUID>                       # full member list
```

### Maintenance

The graph self-maintains via migrations and the verify/rekey/enrich loop. When the user asks for a "checkup":

```bash
ansa paper verify --all --dry-run                    # surface mismatches against Crossref/S2
ansa paper rekey  --all --dry-run                    # propose citekey changes (review before running for real)
ansa fts rebuild                                     # if search results look stale
```

**`rekey` after a bulk `verify` is the canary** — proposed citekey changes that look semantically wrong (e.g. `vaswani2017attention → mineault2025is`) mean verify accepted a bad fuzzy match. Investigate before running real rekey. See `~/code/ansa-kg/CLAUDE.md` "Bulk verify is not idempotent against Crossref drift."

## Resolution helpers

A "paper" in ansa is a UUID. Three input shapes the user might supply:

| User says | Resolve with |
|---|---|
| `019dfbc1-306a-79f1-a79f-56c25aeb1826` | Already a UUID. `ansa node get <id>` to confirm. |
| `vaswani2017attention` | `ansa query '{"type":"paper","where":{"citekey":"vaswani2017attention"}}'` |
| "the attention is all you need paper" | `ansa search "attention all you need"` — pick top hit, confirm with user |

Always echo the resolved UUID + citekey + title back to the user before doing anything mutating.

## Key behaviors

- **One paper at a time.** Never batch-summarize. The user should engage with each paper.
- **Surface candidates after each add.** After a successful import, run `ansa paper similar <new-UUID>` and offer the user 3–5 neighbors that aren't already in the graph.
- **Respect the user's pace.** Present options; let them choose what's next.
- **Only cite what's in the graph.** When answering questions, cite by citekey + UUID. Flag when a question requires papers not in the graph.
- **No new HTTP endpoints from this skill.** If a workflow wants something ansa doesn't expose, note the gap and ask — that's a Phase F+ change to ansa-kg, not orchestrator work.

## Common mistakes

| Mistake | Fix |
|---|---|
| Running `ansa paper rekey --all` without `--dry-run` first | Always dry-run; rekey is an identity change |
| Resolving a citekey/title silently — no user confirmation | Echo UUID + citekey + title before any mutation |
| Citing papers by title only | Use citekeys (`vaswani2017attention`), which match the graph and any downstream BibTeX |
| Trying to read `references/<id>/<id>.pdf` | That layout is gone. Everything is `ansa` over HTTP. |
| Building citation graphs by hand | Deferred to Phase F — `cites` edges aren't populated by importers yet. Use `ansa paper similar` for now. |
