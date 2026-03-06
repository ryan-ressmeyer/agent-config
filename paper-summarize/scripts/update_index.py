#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Update index.yaml with a paper entry.
Safely adds or updates a single paper's metadata in the literature database index.
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import date
from typing import Optional

import yaml


def load_index(index_path: Path) -> dict:
    """Load index.yaml, creating default structure if missing."""
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    if 'papers' not in data:
        data['papers'] = []
    return data


def save_index(index_path: Path, data: dict) -> None:
    """Write index.yaml with consistent formatting."""
    with open(index_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            data, f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def find_entry(papers: list, paper_id: str) -> Optional[int]:
    """Find index of existing entry by ID."""
    for i, p in enumerate(papers):
        if p.get('id') == paper_id:
            return i
    return None


def build_entry(args) -> dict:
    """Build a paper entry dict from CLI arguments."""
    entry = {'id': args.id}

    if args.title:
        entry['title'] = args.title
    if args.authors:
        entry['authors'] = json.loads(args.authors)
    if args.year:
        entry['year'] = int(args.year)
    if args.journal:
        entry['journal'] = args.journal
    if args.doi:
        entry['doi'] = args.doi
    if args.pmid:
        entry['pmid'] = args.pmid
    if args.subject:
        entry['subject'] = json.loads(args.subject)
    if args.summary:
        entry['summary'] = args.summary
    # themes are tracked in themes/*.md synthesis documents, not on individual paper entries
    if args.key_figures:
        entry['key_figures'] = json.loads(args.key_figures)
    if args.status:
        entry['status'] = args.status
    if args.has_pdf is not None:
        entry['has_pdf'] = args.has_pdf.lower() == 'true'
    if args.has_summary is not None:
        entry['has_summary'] = args.has_summary.lower() == 'true'

    return entry


def main():
    parser = argparse.ArgumentParser(
        description='Add or update a paper entry in index.yaml',
        epilog='Example: uv run update_index.py --database references/ --id smith-jones-2019 --title "Paper Title" --year 2019'
    )

    parser.add_argument('--database', default='references/', help='Database directory (default: references/)')
    parser.add_argument('--id', required=True, help='Paper ID (firstauthor-seniorauthor-year)')
    parser.add_argument('--title', help='Paper title')
    parser.add_argument('--authors', help='Authors as JSON list: \'["Last, First", ...]\'')
    parser.add_argument('--year', help='Publication year')
    parser.add_argument('--journal', help='Journal name')
    parser.add_argument('--doi', help='DOI')
    parser.add_argument('--pmid', help='PubMed ID')
    parser.add_argument('--subject', help='Species/model organism as JSON list: \'["macaque"]\'. NOT for topic keywords — use themes for that.')
    parser.add_argument('--summary', help='1-3 sentence summary')

    parser.add_argument('--key-figures', dest='key_figures', help='Key figures as JSON list of {file, caption} dicts')
    parser.add_argument('--status', choices=['to-read', 'read', 'summarized', 'key-paper'], help='Paper status')
    parser.add_argument('--has-pdf', dest='has_pdf', help='Whether PDF exists (true/false)')
    parser.add_argument('--has-summary', dest='has_summary', help='Whether summary exists (true/false)')

    args = parser.parse_args()

    db_path = Path(args.database)
    index_path = db_path / 'index.yaml'

    # Load existing index
    data = load_index(index_path)
    papers = data['papers']

    # Build new entry from args
    new_fields = build_entry(args)

    # Find existing entry
    idx = find_entry(papers, args.id)

    if idx is not None:
        # Update existing entry — merge fields, new values override
        existing = papers[idx]
        existing.update(new_fields)
        papers[idx] = existing
        action = 'Updated'
    else:
        # Add new entry with date_added
        new_fields['date_added'] = str(date.today())
        # Set defaults for missing fields
        new_fields.setdefault('has_pdf', False)
        new_fields.setdefault('has_summary', False)
        new_fields.setdefault('status', 'to-read')
        new_fields.setdefault('subject', [])
        papers.append(new_fields)
        action = 'Added'

    # Save
    save_index(index_path, data)
    print(f'{action} entry for {args.id} in {index_path}', file=sys.stderr)

    # Print the entry as confirmation
    final_idx = find_entry(papers, args.id)
    print(yaml.dump(papers[final_idx], default_flow_style=False, sort_keys=False))


if __name__ == '__main__':
    main()
