#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "pyyaml", "python-dotenv"]
# ///
"""
Fetch citation graph for a paper: references, cited-by, and semantically related papers.
Outputs YAML files for each category, cross-referenced against the local database.
"""

import sys
import os
import re
import json
import argparse
import time
import fcntl
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

S2_RATE_LIMIT_FILE = '/tmp/.s2_last_request'
S2_MIN_INTERVAL = 1.0  # seconds — Semantic Scholar rate limit


def s2_wait():
    """Block until at least S2_MIN_INTERVAL has passed since the last S2 API call."""
    open(S2_RATE_LIMIT_FILE, 'a').close()
    with open(S2_RATE_LIMIT_FILE, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            content = f.read().strip()
            last_time = float(content) if content else 0.0
            now = time.time()
            elapsed = now - last_time
            if 0 < elapsed < S2_MIN_INTERVAL:
                time.sleep(S2_MIN_INTERVAL - elapsed)
            f.seek(0)
            f.truncate()
            f.write(str(time.time()))
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


class CitationGraphFetcher:
    """Fetch citation neighborhoods from Semantic Scholar."""

    S2_BASE = 'https://api.semanticscholar.org/graph/v1'

    def __init__(self):
        self.session = requests.Session()
        api_key = os.getenv('S2_API_KEY', '')
        headers = {'User-Agent': 'LiteratureReview/1.0 (citation-fetch skill)'}
        if api_key:
            headers['x-api-key'] = api_key
        self.session.headers.update(headers)

    def _get_s2_paper_id(self, doi: str) -> str | None:
        """Resolve DOI to Semantic Scholar paper ID."""
        url = f'{self.S2_BASE}/paper/DOI:{doi}'
        params = {'fields': 'paperId,title'}
        try:
            s2_wait()
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json().get('paperId')
            print(f'S2 paper lookup failed: {resp.status_code}', file=sys.stderr)
            return None
        except Exception as e:
            print(f'S2 paper lookup error: {e}', file=sys.stderr)
            return None

    def fetch_references(self, doi: str, limit: int = 100) -> list[dict]:
        """Fetch papers this paper cites."""
        url = f'{self.S2_BASE}/paper/DOI:{doi}/references'
        params = {
            'fields': 'title,authors,year,externalIds',
            'limit': limit,
        }
        return self._fetch_list(url, params, 'citedPaper')

    def fetch_citations(self, doi: str, limit: int = 100) -> list[dict]:
        """Fetch papers that cite this paper."""
        url = f'{self.S2_BASE}/paper/DOI:{doi}/citations'
        params = {
            'fields': 'title,authors,year,externalIds',
            'limit': limit,
        }
        return self._fetch_list(url, params, 'citingPaper')

    def fetch_recommendations(self, doi: str, limit: int = 20) -> list[dict]:
        """Fetch Semantic Scholar recommended papers."""
        s2_id = self._get_s2_paper_id(doi)
        if not s2_id:
            return []
        url = f'https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{s2_id}'
        params = {
            'fields': 'title,authors,year,externalIds,abstract',
            'limit': limit,
        }
        try:
            s2_wait()
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                print(f'S2 recommendations error: {resp.status_code}', file=sys.stderr)
                return []
            papers = resp.json().get('recommendedPapers', [])
            return [self._normalize_paper(p) for p in papers if p.get('title')]
        except Exception as e:
            print(f'S2 recommendations error: {e}', file=sys.stderr)
            return []

    def search_related(self, title: str, limit: int = 10) -> list[dict]:
        """Search S2 for papers with similar keywords (complement to recommendations)."""
        # Extract key terms from title (drop short/common words)
        stopwords = {'the', 'and', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'were', 'been'}
        words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', title) if w.lower() not in stopwords]
        query = ' '.join(words[:8])
        if not query:
            return []
        url = f'{self.S2_BASE}/paper/search'
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,authors,year,externalIds,abstract',
        }
        try:
            s2_wait()
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                return []
            papers = resp.json().get('data', [])
            return [self._normalize_paper(p) for p in papers if p.get('title')]
        except Exception as e:
            print(f'S2 search error: {e}', file=sys.stderr)
            return []

    def _fetch_list(self, url: str, params: dict, paper_key: str) -> list[dict]:
        """Generic paginated fetch for references/citations."""
        try:
            s2_wait()
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                print(f'S2 API error: {resp.status_code} for {url}', file=sys.stderr)
                return []
            items = resp.json().get('data', [])
            results = []
            for item in items:
                paper = item.get(paper_key, {})
                if paper and paper.get('title'):
                    results.append(self._normalize_paper(paper))
            return results
        except Exception as e:
            print(f'S2 API error: {e}', file=sys.stderr)
            return []

    def _normalize_paper(self, paper: dict) -> dict:
        """Normalize S2 paper to our standard format."""
        ext = paper.get('externalIds') or {}
        authors = []
        for a in paper.get('authors', []):
            name = a.get('name', '')
            parts = name.strip().split()
            if len(parts) >= 2:
                authors.append(f'{parts[-1]}, {" ".join(parts[:-1])}')
            elif parts:
                authors.append(parts[0])
        return {
            'title': paper.get('title', ''),
            'authors': authors,
            'year': paper.get('year'),
            'doi': ext.get('DOI'),
            'pmid': ext.get('PubMed'),
            'arxiv_id': ext.get('ArXiv'),
            'abstract': paper.get('abstract', ''),
        }


def generate_paper_id(paper: dict) -> str | None:
    """Generate firstauthor-seniorauthor-year, or None if insufficient data."""
    authors = paper.get('authors', [])
    year = paper.get('year')
    if not authors or not year:
        return None

    def clean(name: str) -> str:
        last = name.split(',')[0].strip() if ',' in name else name.split()[-1]
        return re.sub(r'[^a-z]', '', last.lower()) or 'unknown'

    if len(authors) == 1:
        return f'{clean(authors[0])}-{year}'
    return f'{clean(authors[0])}-{clean(authors[-1])}-{year}'


def load_database_ids(db_path: str) -> set[str]:
    """Load paper IDs and DOIs from database index.yaml."""
    ids = set()
    dois = set()
    index_path = Path(db_path) / 'index.yaml'
    if not index_path.exists():
        return ids
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        for paper in data.get('papers', []):
            if paper.get('id'):
                ids.add(paper['id'])
            if paper.get('doi'):
                dois.add(paper['doi'].lower())
    except Exception as e:
        print(f'Warning: could not load index.yaml: {e}', file=sys.stderr)
    return ids | dois


def check_in_database(paper: dict, db_entries: set[str]) -> bool:
    """Check if a paper is already in the database (by ID or DOI)."""
    pid = generate_paper_id(paper)
    if pid and pid in db_entries:
        return True
    doi = paper.get('doi')
    if doi and doi.lower() in db_entries:
        return True
    return False


def build_entry(paper: dict, in_database: bool, source: str | None = None, relevance: str | None = None) -> dict:
    """Build a YAML-friendly entry for a related paper."""
    entry = {}
    pid = generate_paper_id(paper)
    if pid:
        entry['id'] = pid
    entry['title'] = paper.get('title', '')
    if paper.get('doi'):
        entry['doi'] = paper['doi']
    if paper.get('year'):
        entry['year'] = paper['year']
    entry['in_database'] = in_database
    if source:
        entry['source'] = source
    if relevance:
        entry['relevance'] = relevance
    return entry


def write_yaml(path: Path, key: str, entries: list[dict]) -> None:
    """Write a YAML file with a top-level key."""
    data = {key: entries}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch citation graph: references, cited-by, and related papers',
        epilog='Example: uv run fetch_citation_graph.py --doi 10.xxx --paper-id smith-jones-2019 --output-dir references/smith-jones-2019/',
    )
    parser.add_argument('--doi', required=True, help='DOI of the paper')
    parser.add_argument('--paper-id', required=True, help='Paper ID (firstauthor-seniorauthor-year)')
    parser.add_argument('--output-dir', required=True, help='Output directory for YAML files')
    parser.add_argument('--database-path', default='references/', help='Database path to check in_database (default: references/)')
    parser.add_argument('--ref-limit', type=int, default=100, help='Max references to fetch')
    parser.add_argument('--cite-limit', type=int, default=100, help='Max citations to fetch')
    parser.add_argument('--related-limit', type=int, default=20, help='Max related papers')
    parser.add_argument('--title', default='', help='Paper title (for keyword search of related papers)')
    args = parser.parse_args()

    fetcher = CitationGraphFetcher()
    db_entries = load_database_ids(args.database_path)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── References (papers this paper cites) ──
    print(f'Fetching references for DOI:{args.doi}...', file=sys.stderr)
    refs = fetcher.fetch_references(args.doi, limit=args.ref_limit)
    ref_entries = [build_entry(p, check_in_database(p, db_entries)) for p in refs]
    write_yaml(out_dir / 'references.yaml', 'references', ref_entries)
    print(f'  Found {len(ref_entries)} references', file=sys.stderr)

    # ── Citations (papers that cite this paper) ──
    print(f'Fetching citations...', file=sys.stderr)
    cites = fetcher.fetch_citations(args.doi, limit=args.cite_limit)
    cite_entries = [build_entry(p, check_in_database(p, db_entries)) for p in cites]
    write_yaml(out_dir / 'cited-by.yaml', 'cited_by', cite_entries)
    print(f'  Found {len(cite_entries)} citing papers', file=sys.stderr)

    # ── Related (recommendations + keyword search) ──
    print(f'Fetching related papers...', file=sys.stderr)
    # Recommendations
    recs = fetcher.fetch_recommendations(args.doi, limit=args.related_limit)
    # Keyword search
    title = args.title
    if not title:
        # Try to get title from refs metadata (first entry often self-referential context)
        # Fall back to using DOI lookup
        s2_wait()
        title_resp = fetcher.session.get(
            f'{fetcher.S2_BASE}/paper/DOI:{args.doi}',
            params={'fields': 'title'}, timeout=10,
        )
        if title_resp.status_code == 200:
            title = title_resp.json().get('title', '')

    search_results = fetcher.search_related(title, limit=args.related_limit) if title else []

    # Deduplicate related papers (by DOI or title)
    seen_dois = set()
    seen_titles = set()
    related_entries = []

    # Exclude papers already in refs or cites
    for e in ref_entries + cite_entries:
        if e.get('doi'):
            seen_dois.add(e['doi'].lower())
        seen_titles.add(e.get('title', '').lower().strip())

    for paper in recs:
        doi_lower = (paper.get('doi') or '').lower()
        title_lower = paper.get('title', '').lower().strip()
        if doi_lower and doi_lower in seen_dois:
            continue
        if title_lower in seen_titles:
            continue
        if doi_lower:
            seen_dois.add(doi_lower)
        seen_titles.add(title_lower)
        relevance = ''
        if paper.get('abstract'):
            # Brief relevance note from abstract
            abstract = paper['abstract'][:200]
            relevance = abstract.rstrip('.') + '...' if len(paper['abstract']) > 200 else paper['abstract']
        entry = build_entry(paper, check_in_database(paper, db_entries),
                           source='semantic-scholar-recommended', relevance=relevance)
        related_entries.append(entry)

    for paper in search_results:
        doi_lower = (paper.get('doi') or '').lower()
        title_lower = paper.get('title', '').lower().strip()
        if doi_lower and doi_lower in seen_dois:
            continue
        if title_lower in seen_titles:
            continue
        if doi_lower:
            seen_dois.add(doi_lower)
        seen_titles.add(title_lower)
        relevance = ''
        if paper.get('abstract'):
            abstract = paper['abstract'][:200]
            relevance = abstract.rstrip('.') + '...' if len(paper['abstract']) > 200 else paper['abstract']
        entry = build_entry(paper, check_in_database(paper, db_entries),
                           source='scholar-search', relevance=relevance)
        related_entries.append(entry)

    write_yaml(out_dir / 'related.yaml', 'related', related_entries)
    print(f'  Found {len(related_entries)} related papers (deduplicated)', file=sys.stderr)

    # Summary
    in_db_refs = sum(1 for e in ref_entries if e.get('in_database'))
    in_db_cites = sum(1 for e in cite_entries if e.get('in_database'))
    in_db_related = sum(1 for e in related_entries if e.get('in_database'))
    print(f'\nSummary for {args.paper_id}:', file=sys.stderr)
    print(f'  References: {len(ref_entries)} ({in_db_refs} in database)', file=sys.stderr)
    print(f'  Cited by:   {len(cite_entries)} ({in_db_cites} in database)', file=sys.stderr)
    print(f'  Related:    {len(related_entries)} ({in_db_related} in database)', file=sys.stderr)

    # Output JSON summary to stdout
    summary = {
        'paper_id': args.paper_id,
        'references_count': len(ref_entries),
        'citations_count': len(cite_entries),
        'related_count': len(related_entries),
        'in_database': {
            'references': in_db_refs,
            'citations': in_db_cites,
            'related': in_db_related,
        },
        'candidates_not_in_database': {
            'references': len(ref_entries) - in_db_refs,
            'citations': len(cite_entries) - in_db_cites,
            'related': len(related_entries) - in_db_related,
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
