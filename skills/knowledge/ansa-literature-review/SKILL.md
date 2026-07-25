---
name: ansa-literature-review
description: Use when building or expanding the literature knowledge graph, adding papers, asking what papers are available on a topic, finding related work, summarizing a paper, or synthesizing themes across papers. Routes literature-review work through ANSA and its paper-summarize and theme-synthesize workflows.
---

# ANSA Literature Review

## Purpose

Guide an interactive literature review backed by ANSA. The user controls which papers enter the graph and when they are summarized or synthesized. The agent handles retrieval, metadata, candidate discovery, and routing between literature workflows.

Load `ansa-reference` before using ANSA. It supplies current access, graph, paper, note, collection, citation, PDF, query, and maintenance guidance. Discover exact commands from the active daemon rather than relying on a copied command catalogue.

## Session start

1. Confirm the configured ANSA remote is reachable with one bounded request.
2. Identify the user's requested mode: add, search/question, external discovery, summarize, or synthesize.
3. Resolve every supplied paper identifier to UUID, citekey, and title. Confirm fuzzy matches before mutation.

**Complete when:** ANSA connectivity is known, the requested mode is selected, and every paper needed for the next action is either resolved unambiguously or awaiting one explicit user choice.

## Add a paper

1. Resolve the supplied DOI, PMID, arXiv ID, BibTeX entry, or local PDF through the deployed `ansa paper import` interface.

   **Complete when:** the import either returns a paper UUID and citekey or reports a specific import failure without creating an uncertain duplicate.

2. Inspect the import's metadata, enrichment, and PDF-fetch result. Report the paper UUID and citekey. If public PDF retrieval returned `no_candidates` or `all_failed`, briefly report the attempted sources and ask for a user-supplied PDF.

   Never retrieve papers from Sci-Hub or similar sources.

   **Complete when:** the user knows whether metadata, text, and a PDF are available and has a concrete PDF fallback when needed.

3. Offer the user the next choices: summarize the paper, inspect semantic/citation neighbors, add it to a collection, or stop.

   **Complete when:** the user has selected the next action or ended the workflow.

## Search and question mode

1. Search titles, abstracts, scratchpads, notes, and collections with ANSA full-text search. Use structured query only for exact top-level fields.

   **Complete when:** a bounded candidate set is available or the absence of matching graph content is explicit.

2. Read relevant scratchpads before answering. The user's summaries outrank abstracts. Verify citekeys and UUIDs for every paper used.

   **Complete when:** each substantive literature claim in the answer is traceable to a paper in the graph, identified by citekey and UUID.

3. State the graph's coverage limit. If the question asks what the broader field says, distinguish the graph-backed answer from missing external literature and offer external discovery.

   **Complete when:** the answer names its evidence boundary and does not imply field-wide coverage from a partial graph.

## External discovery

Use the bundled uv/PEP 723 scripts in `scripts/` for papers not yet in ANSA. They emit JSON Lines with a common candidate schema and can mark or exclude papers already in the graph.

```bash
SKILL=~/.agents/skills/ansa-literature-review/scripts

"$SKILL/openalex_search.py" "topic phrase" --per-page 50 --new-only -o candidates.jsonl
"$SKILL/openalex_neighbors.py" --doi 10.xxx --mode both --new-only -o neighbors.jsonl
"$SKILL/s2_recommendations.py" --doi-list seeds.txt --limit 50 --new-only -o recommendations.jsonl
```

`ANSA_CONTACT_EMAIL` overrides the OpenAlex polite-pool contact. `S2_API_KEY` may be supplied when Semantic Scholar rate limits anonymous requests.

1. Confirm the topic and any seed papers with the user.

   **Complete when:** the search question and seed UUIDs/DOIs are explicit.

2. Run only the discovery sources needed for breadth, citation adjacency, or recommendation ranking. Pool and deduplicate candidates by DOI.

   **Complete when:** one deduplicated candidate set records title, authors, year, venue, citation count, abstract snippet, and whether each paper is already in ANSA.

3. Present at most 20 candidates for add/skip/maybe triage. Do not import before the user accepts candidates.

   **Complete when:** every presented candidate has a user disposition or remains explicitly undecided.

4. Import accepted papers and attach them to the requested collection. Summarize papers one at a time unless the user explicitly requests parallel delegation.

   **Complete when:** every accepted paper is either imported and attached, reported as an existing graph paper, or associated with a specific failed import.

## Summarize a paper

Resolve the paper, confirm ambiguous matches, and invoke `paper-summarize`. Do not batch-summarize by default; the user should engage with each paper.

**Complete when:** `paper-summarize` has updated or deliberately preserved the scratchpad and presented the summary for review.

## Synthesize a theme

Resolve the candidate paper set from a user list, search results, or collection membership, then invoke `theme-synthesize`. Do not synthesize papers whose scratchpads are empty.

**Complete when:** the theme's member set is explicit and `theme-synthesize` has created or updated its single synthesis note for user review.

## Behavioral constraints

- Respect the user's pace; present choices rather than automatically expanding the graph.
- Only cite papers verified in ANSA. Flag evidence gaps instead of fabricating citations.
- Surface a few relevant semantic or citation neighbors after an import, but do not add them without approval.
- Confirm UUID, citekey, and title before mutating a paper resolved from fuzzy text.
- Treat ANSA rough edges as feature recommendations for `~/repos/ansa-kg/`; do not invent endpoints or silently patch around missing interfaces.
