---
name: ansa-literature-review
description: Use when building or expanding the literature knowledge graph, adding papers (DOI/PMID/arXiv/PDF), asking "what papers do I have on X", searching the database, finding related work, summarizing a paper, or synthesizing themes across papers. Orchestrates the ansa CLI/HTTP surface and delegates to paper-summarize and theme-synthesize.
---

# ansa Literature Review

## Overview

Interactive orchestrator for the ansa knowledge graph. The user drives the pace — the agent routes work to `ansa` CLI commands (which hit the daemon over HTTP) and delegates structured tasks to sub-skills.

**This is not automation.** The user reads each paper and decides what gets added, summarized, or synthesized. The agent handles metadata, search, and the mechanical edges of "where does this fit."

## Remote

Default remote on the user's workstations (totoro, calcifer) is `kamaji` (`http://kamaji:7327`), pre-configured in `~/.config/ansa/remotes.yaml`. All commands below run unmodified — `ansa` resolves the remote from config. To target a different remote, pass `--remote NAME` or set `ANSA_REMOTE`.

If the remote is unreachable (`ansa node ls --type paper --limit 1` errors), stop and tell the user — `pdf-retrieve`-style fallbacks don't matter if the graph is offline.

## Session start

When a session opens, get oriented in one cheap call:

```bash
curl -s http://kamaji:7327/api/manifest | jq '{node_types: [.node_types[].name], edge_types: [.edge_types[].name], plugins: [.plugins[].name]}'
```

That's enough to confirm the remote is live and learn what node/edge types and plugins are loaded. Don't print large dumps.

The `ansa` CLI is a zsh alias (`uv run --project ~/code/ansa-kg ansa`), so `subprocess.run(["ansa", ...])` from Python and non-interactive shells (sub-agents, hooks) will fail with `FileNotFoundError`. **For programmatic access, hit the HTTP API directly** (examples throughout this skill). The CLI is fine when you're driving things interactively from a zsh session.

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

`paper import` fetches metadata (Crossref / arXiv / Semantic Scholar) and, by default, **also makes a best-effort attempt to fetch a public PDF** via tiered resolvers (Unpaywall → Crossref `link` → OpenAlex → Europe PMC → arXiv → bioRxiv/medRxiv). Tier A = published version, Tier B = accepted manuscript, Tier C = preprint; the fetcher stops at the first source that returns a valid PDF. Auto-enrichment (OCR, embedding) runs synchronously after import.

The import response includes `pdf_fetch.status`:
- `fetched` → check `pdf_fetch.candidate.{source,tier,version,license}` to tell the user where the PDF came from (e.g. "Tier A publishedVersion via Unpaywall, CC-BY"). Provenance is also stored on `properties.pdf.fetched_from`.
- `no_candidates` / `all_failed` → no public copy was found, or every candidate failed validation. The metadata still imported successfully.

**Disable per-import** with `--no-fetch-pdf` (e.g. when the user already has the PDF and just wants metadata first).

**Retry after the fact** for any paper that ended up without a PDF:

```bash
ansa paper fetch-pdf --id <UUID>           # single paper
ansa paper fetch-pdf --all-missing         # every paper without a PDF
ansa paper fetch-pdf --all-missing --limit 20 --tiers A,B   # published/accepted only, no preprints
```

`fetch-pdf` is idempotent (skips when `properties.pdf.path` is already set unless `--force`), records per-source attempt logs in `_raw.pdf_fetch.candidates_tried`, and never raises on resolver/network errors — failures are surfaced in the response, not as exceptions.

**When auto-fetch returned `no_candidates` or `all_failed`, proactively ask the user for a PDF.** Don't wait for them to bring it up — the user often has institutional access or a copy on disk. Phrase it concretely so they know exactly what to do:

> I imported `<citekey>` (`<UUID>`) but the auto-fetcher couldn't find a public PDF (`<status>`, tried N sources). If you can grab one from https://doi.org/<doi> (or you already have it locally), drop the path or attach the file and I'll run:
>
> `ansa paper set-pdf <UUID> /path/to/file.pdf`

When `status == "all_failed"`, briefly summarize *what was tried* from `candidates_tried` (source, tier, http_status / error) — it tells the user whether the paper looked promising-but-blocked vs. genuinely unindexed, which helps them decide how hard to chase it.

Never download from sci-hub or similar — only the tiered resolvers' OA copies and user-supplied files.

After import, surface the new paper's UUID and citekey to the user and ask whether to summarize it now (→ delegate to `paper-summarize`).

### External discovery (papers not yet in the graph)

Trigger: "find related work outside the graph", "what's been cited by paper X?", "build a literature review on topic Y".

ansa only knows about papers already imported. To surface candidates outside the graph, this skill ships three small uv-PEP-723 scripts in `scripts/` (next to this file). All three emit **JSON Lines** with a uniform schema (`doi, title, year, authors, journal, citation_count, abstract, in_graph, ansa_id, ansa_citekey`) and dedup against ansa automatically. Use `--new-only` to drop already-imported hits.

```bash
SKILL=~/.claude/skills/ansa-literature-review/scripts

# Topic search via OpenAlex (free, no key)
"$SKILL/openalex_search.py" "saccadic suppression magnocellular LGN" --per-page 50 --new-only -o cand_topic.jsonl

# Walk references / cited-by for a seed paper (DOI or OpenAlex W-id)
"$SKILL/openalex_neighbors.py" --doi 10.1016/s0896-6273\(02\)00823-1 --mode cited-by --limit 100 --new-only -o cand_citedby.jsonl
"$SKILL/openalex_neighbors.py" --doi 10.xxx --mode references --limit 50 --new-only
"$SKILL/openalex_neighbors.py" --doi 10.xxx --mode both --new-only

# Semantic Scholar recommendations — pooled across multiple seeds
"$SKILL/s2_recommendations.py" --doi-list seeds.txt --limit 50 --new-only -o cand_s2.jsonl
"$SKILL/s2_recommendations.py" --doi 10.xxx --limit 30 --new-only
```

Polite-pool email defaults to `ryan.ressmeyer@gmail.com`; override with `ANSA_CONTACT_EMAIL`. Set `S2_API_KEY` if rate-limited.

**Workflow for building a thematic collection from scratch**:

1. Confirm with the user which papers in the graph are the **seeds**.
2. For each seed, run `openalex_neighbors.py --mode both --new-only`. Pool the resulting JSONL files.
3. Optionally: `openalex_search.py "<topic phrase>" --new-only` for breadth, and `s2_recommendations.py --doi-list seeds.txt --new-only` for a second-opinion ranking.
4. Concatenate JSONL streams, dedup by DOI, rank by relevance (high citation count + topic match in title/abstract).
5. Present the user a short triage list (≤20 candidates). For each, show `title — authors (year) — journal — citations — abstract snippet`. Let them say add/skip/maybe.
6. Batch-import accepted DOIs with `ansa paper import --doi`. Auto-fetch handles PDFs.
7. Add each imported paper to the target collection with `ansa collection add-member <COLL_ID> <PAPER_UUID>`.
8. Delegate summarization in parallel — see "Parallel sub-agent delegation" below.

### Parallel sub-agent delegation

When N papers need summaries, spawn N **general-purpose sub-agents** in a single message (one Agent block per paper). This keeps PDF text out of the main agent's context.

Per-agent prompt template:

```
You are summarizing one paper for the ansa graph. Paper UUID: <UUID>.
Citekey: <citekey>. Title: <title>.

1. Invoke the `paper-summarize` skill to write a full QLMRI summary to
   the paper's scratchpad (this writes to ansa via HTTP).
2. After writing, return ONLY the following stance digest (≤180 words):
   - Question (1 sentence)
   - Method (1 sentence, with key species / N / paradigm)
   - Key result (1–2 sentences)
   - <<Any additional notes that are relevant to the specific task at hand, e.g. "how does this paper relate to topic Y?" or "what's the theme across these papers?">>

Do NOT include PDF text in your response.
```

The main agent receives only the digests, never the PDFs. After all sub-agents complete, the main agent calls `theme-synthesize` on the collection — that skill reads the now-populated scratchpads and writes the synthesis note.

### Search / question mode

Trigger: "what do I have on X?", "find papers about Y", "is there a paper by Author on Z?"

```bash
# Full-text search across title, abstract, authors, notes, collections
ansa search "binocular rivalry temporal dynamics"

# Structured query — CLI takes YAML via `query run`:
ansa query run --inline 'type: paper
where:
  doi: 10.1038/371511a0
limit: 2'

# Semantic neighbors of a paper (embedding cosine over title+abstract)
ansa paper similar <UUID>

# Citation neighbors: papers this one cites, and papers that cite it.
# Use `/api/nodes/<UUID>/neighbors` and filter to edge type `cites`.
# Edges are auto-extracted on import from cached Crossref reference lists
# (Phase F); they cover DOI-tagged references only. References to papers
# not yet in the graph land as `cite_candidate` nodes — list via:
ansa query run --inline 'type: cite_candidate
limit: 50'
```

**`where` only matches indexed top-level columns** on a node (e.g. `doi`, `citekey`, `year`, `title` for `paper`). Deep keys under `properties._raw.*` are NOT filterable — pull the candidate set first, then filter client-side.

**Note bodies**: `ansa note show <NOTE_ID>` returns JSON with both `properties` (which has a `file_ref` body pointer) and a top-level `body` field — that top-level `body` is the markdown string. The HTTP equivalent is `GET /api/notes/{id}`; note that `/api/notes/{id}/body` and `/api/nodes/{id}/body` do NOT exist (they return the SvelteKit shell rather than 404).

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
ansa paper fetch-pdf --all-missing --limit 50        # backfill PDFs for papers imported before auto-fetch existed
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
- **Surface candidates after each add.** After a successful import, run `ansa paper similar <new-UUID>` and offer the user 3–5 neighbors that aren't already in the graph. Citation neighbors (the `cites` edges materialized from the new paper's Crossref references) are also worth a glance — they often surface foundational papers the user might want to pull in.
- **Respect the user's pace.** Present options; let them choose what's next.
- **Only cite what's in the graph.** When answering questions, cite by citekey + UUID. Flag when a question requires papers not in the graph.
- **No new HTTP endpoints from this skill.** If a workflow wants something ansa doesn't expose, note the gap and ask — that's a Phase F+ change to ansa-kg, not orchestrator work.
- **The user maintains ansa-kg (`~/code/ansa-kg/`).** If a task hits a rough surface — awkward workaround, missing flag, repeated manual step, confusing error, a question the CLI/HTTP surface can't answer cleanly — finish the task first, then surface it at the end as a concrete feature recommendation (what was painful, what change would fix it). Don't bury it; don't fix it mid-task either. One-line recommendations are fine; the user decides whether to act.

## Common mistakes

| Mistake | Fix |
|---|---|
| Running `ansa paper rekey --all` without `--dry-run` first | Always dry-run; rekey is an identity change |
| Resolving a citekey/title silently — no user confirmation | Echo UUID + citekey + title before any mutation |
| Citing papers by title only | Use citekeys (`vaswani2017attention`), which match the graph and any downstream BibTeX |
| Trying to read `references/<id>/<id>.pdf` | That layout is gone. Everything is `ansa` over HTTP. |
| Building citation graphs by hand | Done automatically: `cites` edges are extracted from cached Crossref refs on import (Phase F). For backfill / re-extraction use `ansa paper cites extract --id <UUID>` or `--all`. Dangling references live as `cite_candidate` nodes until the target paper is imported. |
