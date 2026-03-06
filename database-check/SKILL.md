---
name: database-check
description: Use when you need to verify literature database integrity, check for missing files, inconsistent metadata, orphaned entries, or sync issues between index.yaml and references.bib
---

# Database Check

## Overview

Verify the structural integrity of the literature database. Checks naming conventions, file presence, cross-references between `index.yaml`/`references.bib`/folder contents, and reports issues with severity levels.

## When to Use

- Before or after adding multiple papers
- User asks to check or clean up the database
- Something seems wrong (missing files, broken references)
- Periodically as maintenance

## Script

### `check_integrity.py` — Full Integrity Check

```bash
# Basic check
uv run ~/.claude/skills/database-check/scripts/check_integrity.py references/

# Verbose output
uv run ~/.claude/skills/database-check/scripts/check_integrity.py references/ --verbose

# Auto-fix trivial issues (has_pdf/has_summary flags, missing bib entries)
uv run ~/.claude/skills/database-check/scripts/check_integrity.py references/ --fix

# Save report
uv run ~/.claude/skills/database-check/scripts/check_integrity.py references/ --output report.json
```

## Checks Performed

| Check | Severity | Auto-fixable |
|-------|----------|-------------|
| Folder name matches `firstauthor-seniorauthor-year` pattern | error | no |
| Folder has `<id>.pdf` and/or `<id>-summary.md` | warning | no |
| Folder exists for each `index.yaml` entry | error | no |
| `index.yaml` entry exists for each folder | error | no |
| `has_pdf` flag matches actual file | warning | yes |
| `has_summary` flag matches actual file | warning | yes |
| Theme files in `themes/` are non-empty | warning | no |
| `references.bib` has entry for each paper | warning | yes (stub) |
| Related papers files have valid structure | warning | no |
| No duplicate DOIs in index | error | no |
| Summary follows QLMRI structure | warning | no |

## Output Format

```json
{
  "stats": {
    "total_papers": 15,
    "papers_with_pdf": 12,
    "papers_with_summary": 10,
    "total_themes": 4,
    "issues_found": 3
  },
  "errors": [...],
  "warnings": [...],
  "auto_fixable": [...]
}
```

## Key Principle

**Never delete files without user confirmation.** Only auto-fix metadata flags and add missing stubs. Destructive operations always require explicit approval.
