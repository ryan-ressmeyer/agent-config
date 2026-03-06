#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Update references.bib with a BibTeX entry.
Safely adds or replaces a single entry identified by its citation key.
"""

import sys
import re
import argparse
from pathlib import Path
def parse_bibtex_keys(content: str) -> dict[str, tuple[int, int]]:
    """
    Parse a BibTeX file and return a dict mapping citation keys
    to (start_pos, end_pos) in the content string.
    """
    entries = {}
    # Match @type{key, ... } — handles nested braces
    pattern = re.compile(r'@\w+\s*\{([^,]+),')

    for match in pattern.finditer(content):
        key = match.group(1).strip()
        start = match.start()
        # Find the matching closing brace
        depth = 0
        pos = match.start()
        while pos < len(content):
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
                if depth == 0:
                    entries[key] = (start, pos + 1)
                    break
            pos += 1

    return entries


def load_bibtex(bib_path: Path) -> str:
    """Load references.bib content, returning empty string if missing."""
    if bib_path.exists():
        return bib_path.read_text(encoding='utf-8')
    return ''


def save_bibtex(bib_path: Path, content: str) -> None:
    """Write references.bib."""
    bib_path.write_text(content, encoding='utf-8')


def add_or_replace_entry(content: str, key: str, new_entry: str) -> str:
    """Add or replace a BibTeX entry in the content."""
    entries = parse_bibtex_keys(content)

    if key in entries:
        # Replace existing entry
        start, end = entries[key]
        content = content[:start] + new_entry + content[end:]
    else:
        # Append new entry
        if content and not content.endswith('\n'):
            content += '\n'
        if content and not content.endswith('\n\n'):
            content += '\n'
        content += new_entry + '\n'

    return content


def main():
    parser = argparse.ArgumentParser(
        description='Add or update a BibTeX entry in references.bib',
        epilog='Example: uv run update_bibtex.py --database references/ --id smith-jones-2019 --entry \'@article{...}\''
    )

    parser.add_argument('--database', default='references/', help='Database directory (default: references/)')
    parser.add_argument('--id', required=True, help='Citation key (paper ID)')
    parser.add_argument('--entry', help='Complete BibTeX entry string')
    parser.add_argument('--entry-file', help='File containing BibTeX entry')

    args = parser.parse_args()

    # Get BibTeX entry
    if args.entry:
        new_entry = args.entry.strip()
    elif args.entry_file:
        entry_path = Path(args.entry_file)
        if not entry_path.exists():
            print(f'Error: Entry file not found: {args.entry_file}', file=sys.stderr)
            sys.exit(1)
        new_entry = entry_path.read_text(encoding='utf-8').strip()
    else:
        # Read from stdin
        new_entry = sys.stdin.read().strip()

    if not new_entry:
        print('Error: No BibTeX entry provided', file=sys.stderr)
        sys.exit(1)

    # Verify the entry contains the expected key
    key_match = re.search(r'@\w+\s*\{([^,]+),', new_entry)
    if not key_match:
        print('Error: Could not parse citation key from BibTeX entry', file=sys.stderr)
        sys.exit(1)

    entry_key = key_match.group(1).strip()
    if entry_key != args.id:
        # Fix the key to match the expected ID
        new_entry = new_entry.replace(entry_key, args.id, 1)
        print(f'Note: Replaced citation key "{entry_key}" with "{args.id}"', file=sys.stderr)

    db_path = Path(args.database)
    bib_path = db_path / 'references.bib'

    # Load, update, save
    content = load_bibtex(bib_path)
    content = add_or_replace_entry(content, args.id, new_entry)
    save_bibtex(bib_path, content)

    print(f'Wrote entry for {args.id} in {bib_path}', file=sys.stderr)
    print(new_entry)


if __name__ == '__main__':
    main()
