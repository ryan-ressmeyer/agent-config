---
name: pdf-retrieve
description: Use when you need to obtain a PDF for a paper and place it in the literature database, checking open-access sources first and asking the user when paywalled
---

# PDF Retrieve

## Overview

Find and download paper PDFs, checking open-access sources first. If no open-access version exists, ask the user to retrieve it manually. Never silently fail on paywalls.

## When to Use

- A paper has been added to the database but lacks a PDF
- User provides a DOI/PMID and wants the full text
- Processing a paper that needs to be read for summarization

## Script

### `find_open_access.py` — Find PDF URLs

```bash
# Basic usage
uv run ~/.claude/skills/pdf-retrieve/scripts/find_open_access.py --doi 10.1523/JNEUROSCI.1234-19.2019

# With additional identifiers for better coverage
uv run ~/.claude/skills/pdf-retrieve/scripts/find_open_access.py \
  --doi 10.1523/JNEUROSCI.1234-19.2019 \
  --pmid 31234567 \
  --arxiv 2103.14030 \
  --email user@university.edu
```

**Output:** JSON with all found PDF URLs and a recommended best URL.

**Does NOT download** — just finds URLs. Download with:
```bash
curl -L -o references/<id>/<id>.pdf "<pdf_url>"
```

## Source Priority

Checked in this order:

1. **Unpaywall** — Legal open-access lookup by DOI. Requires email (set `UNPAYWALL_EMAIL` env var or `--email` flag).
2. **PubMed Central** — Free full text for NIH-funded research. Uses PMID to check for PMC availability.
3. **arXiv / bioRxiv / medRxiv** — If preprint ID is known, PDF URL is deterministic.
4. **Semantic Scholar** — Checks `openAccessPdf` field.

## When No Open Access Found

**Do not try to bypass paywalls.** Instead:

1. Tell the user: "I couldn't find an open-access PDF for this paper."
2. Provide the DOI link: `https://doi.org/10.xxx/yyy`
3. Tell them where to put it: `references/<id>/<id>.pdf`
4. Wait for confirmation before proceeding

Example message:
> I couldn't find an open-access PDF for Smith & Jones (2019).
>
> - DOI link: https://doi.org/10.1523/JNEUROSCI.1234-19.2019
> - Please download and save to: `references/smith-jones-2019/smith-jones-2019.pdf`
>
> Let me know when it's ready and I'll proceed with the summary.

## PDF Validation

After downloading, verify:
- File exists and is non-empty
- Starts with `%PDF` header (not HTML from a login page)
- File size is reasonable (>10KB for a real paper)

```bash
# Quick validation
head -c 4 references/<id>/<id>.pdf  # Should show %PDF
wc -c references/<id>/<id>.pdf      # Should be >10KB
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Downloading HTML login page as "PDF" | Always validate %PDF header |
| Silently failing when paywalled | Always tell the user and provide the DOI link |
| Not checking all sources | Run find_open_access.py which checks all four |
| Forgetting to update has_pdf in index | Run update_index.py after successful download |
