---
name: ansa-reference
description: Use when a task needs facts or usage guidance about ANSA, including remotes, CLI or HTTP access, graph concepts, papers, notes, collections, themes, citations, PDF handling, queries, or database maintenance.
---

# ANSA Reference

ANSA is a plugin-driven knowledge graph with a CLI and HTTP API over the same daemon. It is the backing store for Ryan's literature graph, but its graph, client, and operational conventions also apply outside literature-review workflows.

## Authority and discovery

The active daemon is authoritative for its loaded types, plugins, and commands:

- `GET /api/manifest` — loaded node types, edge types, and plugins.
- `GET /api/commands` — current machine-readable CLI command tree.
- `ansa --help` and nested `--help` — current installed CLI surface.
- `~/.config/ansa/remotes.yaml` — configured remotes and default selection.

The local source checkout is `~/repos/ansa-kg/`. Use these files when implementation detail is required:

- `README.md` — architecture, installation, and remote-client overview.
- `packages/ansa-api/src/ansa_api/command_specs.py` — core command specifications.
- `packages/ansa-api/src/ansa_api/routes.py` — core HTTP routes.
- `plugins/ansa-papers/src/ansa_papers/{command_specs.py,api.py}` — paper commands and routes.
- `plugins/ansa-notes/src/ansa_notes/{command_specs.py,api.py}` — note commands and routes.
- `plugins/ansa-collections/src/ansa_collections/{command_specs.py,api.py}` — collection commands and routes.

Prefer runtime discovery over copying complete command or endpoint tables into skills. The deployed daemon and local checkout may be on different revisions; check the daemon before relying on source-only behavior.

## Access and remotes

`ansa` is installed as a uv tool and is available to interactive and non-interactive processes. The usual remote is named `kamaji`; resolve its URL from `~/.config/ansa/remotes.yaml` rather than hard-coding it. Select another remote with `--remote NAME` or `ANSA_REMOTE=NAME`.

The CLI rebuilds plugin commands from `/api/commands`, so a client does not need local copies of the server's plugins. For scripts, either invoke the real `ansa` executable or use `ansa_cli.client.Client` against the configured HTTP URL.

A cheap orientation check is:

```bash
ansa node list --type paper --limit 1
```

For type/plugin discovery without a large data response, inspect `/api/manifest`. If the remote is unavailable, ANSA-backed work cannot proceed; report the connection failure rather than inventing a filesystem fallback.

## Graph concepts

- A node has a UUID, type, indexed top-level fields, and additional properties.
- Edges connect source and target UUIDs and have an edge type.
- Plugins register node types, edge types, commands, routes, and storage roots.
- Full-text search and structured query are different operations.
- File-backed values such as paper PDFs, extracted text, note bodies, and attachments may be represented by `file_ref` metadata rather than inline bytes.

Structured `where` clauses operate on queryable top-level fields. Deep values under raw provider payloads such as `properties._raw.*` are not generally filterable; retrieve a bounded candidate set and filter those values client-side.

The current structured-query CLI accepts YAML:

```bash
ansa query run --inline 'type: paper
where:
  citekey: vaswani2017attention
limit: 2'
```

Use `ansa search "terms"` for full-text retrieval and `ansa node get <UUID>` for an exact node.

## Papers and identifiers

A paper's durable graph identity is its UUID. A citekey is a human-readable property used in notes and downstream citations. DOI, PMID, arXiv ID, citekey, title fragments, and UUIDs are lookup inputs, not interchangeable identities.

Resolution conventions:

| Input | Lookup |
|---|---|
| UUID | `ansa node get <UUID>` |
| citekey | structured paper query on `citekey` |
| title or author fragment | `ansa search "..."` |

Fuzzy title resolution can return near-matches. Before mutating a paper, report its UUID, citekey, and title and confirm ambiguous matches.

Paper import supports identifiers and local files through the dynamically registered `paper import` command. Consult `ansa paper import --help` for the deployed flags. Imports resolve metadata and may run enrichment such as text extraction, OCR, embeddings, citation extraction, and public-PDF discovery.

## Public PDF handling

Best-effort PDF discovery uses legitimate public sources such as Unpaywall, publisher/Crossref links, OpenAlex, Europe PMC, arXiv, and bioRxiv/medRxiv. Do not use Sci-Hub or similar sources.

Import responses may distinguish:

- `fetched` — a public candidate was retrieved and validated.
- `no_candidates` — no eligible public candidate was found.
- `all_failed` — candidates existed but failed retrieval or validation.

When available, candidate source, tier, version, license, and attempted-source records explain provenance and failure. Metadata import can succeed even when PDF retrieval fails. User-supplied PDFs remain the appropriate fallback.

PDF and extracted-text properties are commonly `file_ref` records. Fetch their bytes through the paper plugin's storage/client methods; do not treat the property dictionary as document content.

## Scratchpads and notes

A paper scratchpad is the user's QLMRI summary and working note. It is accessed through the paper scratchpad command or `/api/papers/{paper_id}/scratchpad`. Scratchpads may auto-create a heading-only stub on first read; a body containing more than the stub is user content and should not be overwritten without review.

A general note is a node whose body is file-backed. `GET /api/notes/{note_id}` returns note metadata plus a top-level `body` string. There is no `/api/notes/{id}/body` or `/api/nodes/{id}/body` route.

Notes attached to a node are listed at `GET /api/nodes/{node_id}/notes`. In rendered markdown, link graph nodes as `[label](/nodes/<uuid>)`.

## Collections and themes

Collections group nodes through membership edges. A literature theme uses:

- a `collection` with `properties.kind = "theme"`;
- paper membership represented by `in_collection` edges;
- one synthesis `note` attached to the collection through `note_of`.

The collection membership is authoritative. Do not duplicate the member list inside the synthesis body. Updating a theme normally updates the existing synthesis note rather than creating another note.

## Citations and related work

Paper citation extraction materializes `cites` edges for resolvable references. DOI-bearing references not yet represented as papers may appear as `cite_candidate` nodes. Semantic similarity and citation adjacency answer different questions: similarity compares indexed text/embeddings, while citation neighbors follow graph edges.

Use runtime command discovery for current citation extraction, reconciliation, and neighbor flags. Do not reconstruct citation graphs manually when ANSA already exposes the relationships.

## Maintenance guidance

ANSA applies database migrations through its service lifecycle. Operational maintenance includes metadata verification, citekey review, PDF backfill, enrichment, citation reconciliation, storage garbage collection, and FTS rebuilds.

Identity-changing operations require review:

- Run bulk verification and rekey operations in dry-run mode first.
- Treat implausible proposed citekey changes as evidence of a bad metadata match.
- Investigate the matched DOI/title/authors before accepting a rekey.
- Do not run a real bulk rekey merely because the command completed successfully.

Use `ansa paper ... --help`, `ansa fts --help`, and `/api/commands` for current maintenance syntax. Rebuild FTS only when status or observed search behavior indicates stale indexing. Storage garbage collection should be inspected before pruning.

## Limits and failure reporting

Do not invent HTTP endpoints or undocumented response fields. If the CLI/API cannot answer a task cleanly, finish any safe portion of the user's task, then report the missing operation as a concrete ANSA feature request. Implementation changes belong in `~/repos/ansa-kg/`, not in a workflow skill.
