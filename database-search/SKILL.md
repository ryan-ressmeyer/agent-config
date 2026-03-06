---
name: database-search
description: Use when searching the local literature database for papers by keyword, author, subject, theme, year, or citation graph connections
---

# Database Search

## Overview

Search the local literature database by metadata, full-text content, or citation graph connections. Returns relevant papers ranked by match quality with context snippets.

## When to Use

- Looking for papers on a topic in the database
- Filtering by subject (macaque, mouse, simulation, etc.)
- Finding papers connected to a specific paper (cites, cited-by, related)
- Answering user questions about what's in the database
- Gathering papers for a theme synthesis

## Script

### `search_database.py` — Search Local Database

```bash
# Text search
uv run ~/.claude/skills/database-search/scripts/search_database.py "orientation selectivity" --database references/

# With filters
uv run ~/.claude/skills/database-search/scripts/search_database.py "receptive field" \
  --subject macaque \
  --year-min 2015 \
  --year-max 2023 \
  --database references/

# Filter by author
uv run ~/.claude/skills/database-search/scripts/search_database.py --author "Smith" --database references/

# Citation graph queries
uv run ~/.claude/skills/database-search/scripts/search_database.py --cited-by smith-jones-2019 --database references/
uv run ~/.claude/skills/database-search/scripts/search_database.py --cites smith-jones-2019 --database references/
uv run ~/.claude/skills/database-search/scripts/search_database.py --related-to smith-jones-2019 --database references/
```

## Search Targets

1. **index.yaml** — title, authors, journal, subject, summary
2. **Summary files** — full text of QLMRI summaries
3. **Theme documents** — full text of `themes/*.md`
4. **Citation graph files** — `references.yaml`, `cited-by.yaml`, `related.yaml`

## Output

JSON array of matches, each with:
- Paper `id` and metadata from index
- Relevance score
- Which fields matched
- Context snippets from matched text

## Subject Vocabulary

Common values (not exhaustive): `macaque`, `mouse`, `human`, `cat`, `ferret`, `marmoset`, `rat`, `zebrafish`, `simulation`, `computational-model`, `algorithm`, `theoretical`
