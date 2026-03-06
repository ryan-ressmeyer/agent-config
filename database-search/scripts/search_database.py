#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Search the local literature database by keyword, metadata, or citation graph.
Returns matching papers ranked by relevance with context snippets.
"""

import sys
import json
import argparse
from pathlib import Path

import yaml


class DatabaseSearcher:
    """Search the local literature database."""

    def __init__(self, db_path: str):
        self.db = Path(db_path)
        self.papers: list[dict] = []
        self._load_index()

    def _load_index(self):
        index_path = self.db / 'index.yaml'
        if not index_path.exists():
            print(f'Warning: {index_path} not found', file=sys.stderr)
            return
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            self.papers = data.get('papers', [])
        except Exception as e:
            print(f'Error loading index: {e}', file=sys.stderr)

    def search(self, query: str = '', subject: str = '',
               author: str = '', year_min: int = 0, year_max: int = 9999,
               cited_by: str = '', cites: str = '', related_to: str = '') -> list[dict]:
        """Search with query and filters. Returns ranked results."""

        # Citation graph queries (return early)
        if cited_by:
            return self._search_citation_graph(cited_by, 'cited_by', 'cited-by.yaml')
        if cites:
            return self._search_citation_graph(cites, 'references', 'references.yaml')
        if related_to:
            return self._search_citation_graph(related_to, 'related', 'related.yaml')

        results = []
        query_lower = query.lower() if query else ''
        query_terms = query_lower.split() if query_lower else []

        for paper in self.papers:
            year = paper.get('year', 0)
            if year and (year < year_min or year > year_max):
                continue

            # Subject filter
            if subject:
                paper_subjects = paper.get('subject', [])
                if isinstance(paper_subjects, str):
                    paper_subjects = [paper_subjects]
                if not any(subject.lower() in s.lower() for s in paper_subjects):
                    continue

            # Author filter
            if author:
                paper_authors = paper.get('authors', [])
                if not any(author.lower() in a.lower() for a in paper_authors):
                    continue

            # If no query, all remaining papers match (filters only)
            if not query_terms:
                results.append(self._build_result(paper, 1.0, ['filter_match'], {}))
                continue

            # Score based on query term matches across fields
            score = 0.0
            matched_fields = []
            snippets = {}

            # Title (high weight)
            title = (paper.get('title') or '').lower()
            title_hits = sum(1 for t in query_terms if t in title)
            if title_hits:
                score += title_hits * 3.0
                matched_fields.append('title')
                snippets['title'] = paper.get('title', '')

            # Summary
            summary = (paper.get('summary') or '').lower()
            summary_hits = sum(1 for t in query_terms if t in summary)
            if summary_hits:
                score += summary_hits * 2.0
                matched_fields.append('summary')
                snippets['summary'] = paper.get('summary', '')

            # Authors
            authors_str = ' '.join(paper.get('authors', [])).lower()
            if any(t in authors_str for t in query_terms):
                score += 1.0
                matched_fields.append('authors')

            # Journal
            journal = (paper.get('journal') or '').lower()
            if any(t in journal for t in query_terms):
                score += 0.5
                matched_fields.append('journal')

            # Full-text summary search
            pid = paper.get('id', '')
            summary_path = self.db / pid / f'{pid}-summary.md'
            if summary_path.exists() and score == 0:
                # Only search full text if metadata didn't match
                try:
                    content = summary_path.read_text(encoding='utf-8').lower()
                    full_hits = sum(1 for t in query_terms if t in content)
                    if full_hits:
                        score += full_hits * 1.0
                        matched_fields.append('full_summary')
                        # Extract snippet around first match
                        for term in query_terms:
                            idx = content.find(term)
                            if idx >= 0:
                                start = max(0, idx - 60)
                                end = min(len(content), idx + len(term) + 60)
                                snippets['full_summary'] = '...' + content[start:end].strip() + '...'
                                break
                except Exception:
                    pass

            if score > 0:
                results.append(self._build_result(paper, score, matched_fields, snippets))

        # Also search theme documents
        if query_terms:
            theme_results = self._search_themes(query_terms)
            results.extend(theme_results)

        # Sort by score descending
        results.sort(key=lambda r: r['score'], reverse=True)
        return results

    def _search_citation_graph(self, paper_id: str, yaml_key: str, filename: str) -> list[dict]:
        """Find papers connected to a given paper via citation graph files."""
        folder = self.db / paper_id
        fpath = folder / filename
        if not fpath.exists():
            print(f'No {filename} found for {paper_id}', file=sys.stderr)
            return []
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            entries = data.get(yaml_key, [])
            results = []
            for entry in entries:
                result = {
                    'id': entry.get('id', ''),
                    'title': entry.get('title', ''),
                    'year': entry.get('year'),
                    'doi': entry.get('doi', ''),
                    'in_database': entry.get('in_database', False),
                    'score': 1.0,
                    'matched_fields': [f'{yaml_key}_of_{paper_id}'],
                    'snippets': {},
                }
                if entry.get('relevance'):
                    result['snippets']['relevance'] = entry['relevance']
                if entry.get('source'):
                    result['source'] = entry['source']
                results.append(result)
            return results
        except Exception as e:
            print(f'Error reading {fpath}: {e}', file=sys.stderr)
            return []

    def _search_themes(self, query_terms: list[str]) -> list[dict]:
        """Search theme documents for query terms."""
        themes_dir = self.db / 'themes'
        if not themes_dir.exists():
            return []
        results = []
        for theme_file in themes_dir.glob('*.md'):
            try:
                content = theme_file.read_text(encoding='utf-8').lower()
                hits = sum(1 for t in query_terms if t in content)
                if hits:
                    # Extract snippet
                    snippet = ''
                    for term in query_terms:
                        idx = content.find(term)
                        if idx >= 0:
                            start = max(0, idx - 60)
                            end = min(len(content), idx + len(term) + 60)
                            snippet = '...' + content[start:end].strip() + '...'
                            break
                    results.append({
                        'id': f'theme:{theme_file.stem}',
                        'title': f'Theme: {theme_file.stem}',
                        'type': 'theme',
                        'score': hits * 0.8,
                        'matched_fields': ['theme_document'],
                        'snippets': {'theme_content': snippet},
                    })
            except Exception:
                pass
        return results

    def _build_result(self, paper: dict, score: float, matched_fields: list, snippets: dict) -> dict:
        return {
            'id': paper.get('id', ''),
            'title': paper.get('title', ''),
            'authors': paper.get('authors', []),
            'year': paper.get('year'),
            'journal': paper.get('journal', ''),
            'subject': paper.get('subject', []),
            'summary': paper.get('summary', ''),
            'status': paper.get('status', ''),
            'has_pdf': paper.get('has_pdf', False),
            'has_summary': paper.get('has_summary', False),
            'score': round(score, 2),
            'matched_fields': matched_fields,
            'snippets': snippets,
        }


def main():
    parser = argparse.ArgumentParser(
        description='Search the local literature database',
        epilog='Example: uv run search_database.py "orientation selectivity" --subject macaque --database references/',
    )
    parser.add_argument('query', nargs='?', default='', help='Search query')
    parser.add_argument('--database', default='references/', help='Database path (default: references/)')
    parser.add_argument('--subject', default='', help='Filter by subject (e.g., macaque, simulation)')
    parser.add_argument('--author', default='', help='Filter by author name')
    parser.add_argument('--year-min', type=int, default=0, help='Minimum year')
    parser.add_argument('--year-max', type=int, default=9999, help='Maximum year')
    parser.add_argument('--cited-by', default='', help='Find papers that cite this paper ID')
    parser.add_argument('--cites', default='', help='Find papers cited by this paper ID')
    parser.add_argument('--related-to', default='', help='Find papers related to this paper ID')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    args = parser.parse_args()

    if not args.query and not any([args.subject, args.author,
                                    args.cited_by, args.cites, args.related_to,
                                    args.year_min > 0, args.year_max < 9999]):
        parser.print_help()
        sys.exit(1)

    searcher = DatabaseSearcher(args.database)
    results = searcher.search(
        query=args.query,
        subject=args.subject,
        author=args.author,
        year_min=args.year_min,
        year_max=args.year_max,
        cited_by=args.cited_by,
        cites=args.cites,
        related_to=args.related_to,
    )

    output_data = {
        'query': args.query,
        'filters': {k: v for k, v in {
            'subject': args.subject, 'theme': args.theme, 'author': args.author,
            'year_min': args.year_min if args.year_min > 0 else None,
            'year_max': args.year_max if args.year_max < 9999 else None,
            'cited_by': args.cited_by, 'cites': args.cites, 'related_to': args.related_to,
        }.items() if v},
        'count': len(results),
        'results': results,
    }

    output = json.dumps(output_data, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote {len(results)} results to {args.output}', file=sys.stderr)
    else:
        print(output)

    print(f'\nFound {len(results)} matching papers', file=sys.stderr)


if __name__ == '__main__':
    main()
