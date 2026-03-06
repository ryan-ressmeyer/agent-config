---
name: citation-fetch
description: Use when you need to retrieve citation metadata for a paper (from DOI, PMID, arXiv ID, title, or search query), generate BibTeX entries, or fetch citation graphs (references, cited-by, and semantically related papers)
---

# Citation Fetch

## Overview

Retrieve full citation metadata and citation neighborhood for a paper. Generates structured data for `index.yaml`, BibTeX entries for `references.bib`, and discovers related papers via citation graph and semantic search.

## When to Use

- Adding a new paper to the literature database
- Looking up metadata for a DOI, PMID, or arXiv ID
- Searching for papers by topic/keywords
- Discovering what a paper cites, what cites it, and what's semantically related

## Scripts

### `fetch_metadata.py` — Retrieve Citation Metadata

```bash
# By DOI
uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --doi 10.1523/JNEUROSCI.1234-19.2019

# By PMID
uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --pmid 31234567

# By arXiv ID
uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --arxiv 2103.14030

# Search by query (returns top results for user to choose)
uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --query "orientation selectivity V1 temporal dynamics"

# Save to file
uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --doi 10.xxx --output metadata.json
```

**Output:** JSON with `id` (firstauthor-seniorauthor-year), `authors`, `title`, `journal`, `year`, `doi`, `pmid`, `abstract`, `volume`, `issue`, `pages`, `bibtex` entry string.

### `fetch_citation_graph.py` — Retrieve Related Papers

```bash
uv run ~/.claude/skills/citation-fetch/scripts/fetch_citation_graph.py \
  --doi 10.1523/JNEUROSCI.1234-19.2019 \
  --paper-id smith-jones-2019 \
  --output-dir references/smith-jones-2019/ \
  --database-path references/
```

**Produces three YAML files:**
- `references.yaml` — papers this paper cites
- `cited-by.yaml` — papers that cite this paper
- `related.yaml` — semantically similar papers (via Semantic Scholar recommendations + keyword search with abstract screening)

Each entry is cross-referenced against the database (`in_database: true/false`).

## API Sources

| Source | Used For | Rate Limit |
|--------|----------|------------|
| CrossRef | DOI → metadata | Polite pool (no key needed) |
| PubMed E-utilities | PMID → metadata | 3/sec (10/sec with API key) |
| arXiv API | arXiv ID → metadata | No explicit limit, be polite |
| Semantic Scholar | Search, citation graph, recommendations | 100/5min (no key), 1/sec with key |

**Environment variables (optional):**
- `NCBI_API_KEY` — for faster PubMed access
- `NCBI_EMAIL` — recommended for PubMed
- `S2_API_KEY` — for higher Semantic Scholar rate limits

## Paper ID Format

Generated automatically: `firstauthor-seniorauthor-year` (all lowercase, hyphens, ASCII only).
- Single author: `author-year`
- Year collision: append letter (`smith-jones-2019b`)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Not checking if paper already in database | Check index.yaml before fetching |
| Accepting first search result blindly | Present results to user, let them choose |
| Missing senior author in ID | Last author is senior author, not second author |
| Using bare python | Always `uv run` |
