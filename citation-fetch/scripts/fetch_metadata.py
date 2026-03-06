#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Fetch citation metadata from DOI, PMID, arXiv ID, or search query.
Returns structured JSON with metadata and a generated paper ID.
"""

import sys
import os
import re
import json
import argparse
import time
import xml.etree.ElementTree as ET

import requests


class MetadataFetcher:
    """Fetch paper metadata from CrossRef, PubMed, arXiv, and Semantic Scholar."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiteratureReview/1.0 (citation-fetch skill)'
        })

    # ── CrossRef (DOI) ──────────────────────────────────────────────

    def fetch_by_doi(self, doi: str) -> dict | None:
        """Fetch metadata from CrossRef API by DOI."""
        doi = self._clean_doi(doi)
        url = f'https://api.crossref.org/works/{doi}'
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f'CrossRef error: status {resp.status_code} for DOI {doi}', file=sys.stderr)
                return None
            msg = resp.json().get('message', {})
            authors = self._authors_crossref(msg.get('author', []))
            year = self._year_crossref(msg)
            return {
                'title': (msg.get('title') or [''])[0],
                'authors': authors,
                'year': int(year) if year else None,
                'journal': (msg.get('container-title') or [''])[0],
                'doi': doi,
                'volume': str(msg.get('volume', '')) or None,
                'issue': str(msg.get('issue', '')) or None,
                'pages': msg.get('page') or None,
                'abstract': msg.get('abstract', ''),
                'publisher': msg.get('publisher', ''),
            }
        except Exception as e:
            print(f'CrossRef error for {doi}: {e}', file=sys.stderr)
            return None

    # ── PubMed (PMID) ──────────────────────────────────────────────

    def fetch_by_pmid(self, pmid: str) -> dict | None:
        """Fetch metadata from PubMed E-utilities by PMID."""
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        params = {'db': 'pubmed', 'id': pmid, 'retmode': 'xml', 'rettype': 'abstract'}
        email = os.getenv('NCBI_EMAIL', '')
        api_key = os.getenv('NCBI_API_KEY', '')
        if email:
            params['email'] = email
        if api_key:
            params['api_key'] = api_key
        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                print(f'PubMed error: status {resp.status_code} for PMID {pmid}', file=sys.stderr)
                return None
            root = ET.fromstring(resp.content)
            article = root.find('.//PubmedArticle')
            if article is None:
                return None
            mc = article.find('.//MedlineCitation')
            art = mc.find('.//Article')
            jnl = art.find('.//Journal')
            # DOI
            doi = None
            for aid in article.findall('.//ArticleId'):
                if aid.get('IdType') == 'doi':
                    doi = aid.text
            # Authors
            authors = []
            for au in art.findall('.//Author'):
                last = au.findtext('.//LastName', '')
                fore = au.findtext('.//ForeName', '')
                if last:
                    authors.append(f'{last}, {fore}' if fore else last)
            # Year
            year = art.findtext('.//Journal/JournalIssue/PubDate/Year', '')
            if not year:
                md = art.findtext('.//Journal/JournalIssue/PubDate/MedlineDate', '')
                m = re.search(r'\d{4}', md or '')
                year = m.group() if m else ''
            return {
                'title': art.findtext('.//ArticleTitle', ''),
                'authors': authors,
                'year': int(year) if year else None,
                'journal': jnl.findtext('.//Title', ''),
                'doi': doi,
                'pmid': pmid,
                'volume': jnl.findtext('.//JournalIssue/Volume') or None,
                'issue': jnl.findtext('.//JournalIssue/Issue') or None,
                'pages': art.findtext('.//Pagination/MedlinePgn') or None,
                'abstract': art.findtext('.//Abstract/AbstractText', ''),
            }
        except Exception as e:
            print(f'PubMed error for {pmid}: {e}', file=sys.stderr)
            return None

    # ── arXiv ───────────────────────────────────────────────────────

    def fetch_by_arxiv(self, arxiv_id: str) -> dict | None:
        """Fetch metadata from arXiv API."""
        url = 'http://export.arxiv.org/api/query'
        params = {'id_list': arxiv_id, 'max_results': 1}
        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                return None
            ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
            root = ET.fromstring(resp.content)
            entry = root.find('a:entry', ns)
            if entry is None:
                return None
            authors = [a.findtext('a:name', '', ns) for a in entry.findall('a:author', ns)]
            # Convert "First Last" to "Last, First"
            formatted_authors = []
            for name in authors:
                parts = name.strip().split()
                if len(parts) >= 2:
                    formatted_authors.append(f'{parts[-1]}, {" ".join(parts[:-1])}')
                elif parts:
                    formatted_authors.append(parts[0])
            published = entry.findtext('a:published', '', ns)
            year = published[:4] if published else None
            doi_el = entry.find('x:doi', ns)
            return {
                'title': entry.findtext('a:title', '', ns).strip().replace('\n', ' '),
                'authors': formatted_authors,
                'year': int(year) if year else None,
                'journal': None,
                'doi': doi_el.text if doi_el is not None else None,
                'arxiv_id': arxiv_id,
                'abstract': entry.findtext('a:summary', '', ns).strip().replace('\n', ' '),
            }
        except Exception as e:
            print(f'arXiv error for {arxiv_id}: {e}', file=sys.stderr)
            return None

    # ── Semantic Scholar (search) ───────────────────────────────────

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search Semantic Scholar for papers matching a query."""
        url = 'https://api.semanticscholar.org/graph/v1/paper/search'
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,authors,year,externalIds,abstract,journal,citationCount',
        }
        api_key = os.getenv('S2_API_KEY', '')
        headers = {}
        if api_key:
            headers['x-api-key'] = api_key
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f'Semantic Scholar search error: {resp.status_code}', file=sys.stderr)
                return []
            data = resp.json()
            results = []
            for paper in data.get('data', []):
                ext = paper.get('externalIds') or {}
                authors = []
                for a in paper.get('authors', []):
                    name = a.get('name', '')
                    parts = name.strip().split()
                    if len(parts) >= 2:
                        authors.append(f'{parts[-1]}, {" ".join(parts[:-1])}')
                    elif parts:
                        authors.append(parts[0])
                results.append({
                    'title': paper.get('title', ''),
                    'authors': authors,
                    'year': paper.get('year'),
                    'journal': (paper.get('journal') or {}).get('name'),
                    'doi': ext.get('DOI'),
                    'pmid': ext.get('PubMed'),
                    'arxiv_id': ext.get('ArXiv'),
                    'abstract': paper.get('abstract', ''),
                    'citation_count': paper.get('citationCount', 0),
                })
            return results
        except Exception as e:
            print(f'Semantic Scholar search error: {e}', file=sys.stderr)
            return []

    # ── Helpers ─────────────────────────────────────────────────────

    def _clean_doi(self, doi: str) -> str:
        doi = doi.strip()
        for prefix in ('https://doi.org/', 'http://doi.org/', 'doi:'):
            if doi.startswith(prefix):
                doi = doi[len(prefix):]
        return doi

    def _authors_crossref(self, authors: list) -> list[str]:
        result = []
        for a in authors:
            family = a.get('family', '')
            given = a.get('given', '')
            if family:
                result.append(f'{family}, {given}' if given else family)
        return result

    def _year_crossref(self, msg: dict) -> str:
        for field in ('published-print', 'published-online', 'created'):
            dp = msg.get(field, {}).get('date-parts', [[]])
            if dp and dp[0]:
                return str(dp[0][0])
        return ''


def generate_paper_id(metadata: dict) -> str:
    """Generate firstauthor-seniorauthor-year ID from metadata."""
    authors = metadata.get('authors', [])
    year = metadata.get('year', 'XXXX')

    def clean_name(name: str) -> str:
        # "Last, First" -> "last"
        last = name.split(',')[0].strip() if ',' in name else name.split()[-1] if name else 'unknown'
        return re.sub(r'[^a-z]', '', last.lower()) or 'unknown'

    if not authors:
        return f'unknown-{year}'
    elif len(authors) == 1:
        return f'{clean_name(authors[0])}-{year}'
    else:
        first = clean_name(authors[0])
        senior = clean_name(authors[-1])
        return f'{first}-{senior}-{year}'


def metadata_to_bibtex(paper_id: str, metadata: dict) -> str:
    """Generate a BibTeX entry string from metadata."""
    entry_type = 'article' if metadata.get('journal') else 'misc'
    lines = [f'@{entry_type}{{{paper_id},']

    if metadata.get('authors'):
        authors_str = ' and '.join(metadata['authors'])
        lines.append(f'  author  = {{{authors_str}}},')
    if metadata.get('title'):
        lines.append(f'  title   = {{{metadata["title"]}}},')
    if metadata.get('journal'):
        lines.append(f'  journal = {{{metadata["journal"]}}},')
    if metadata.get('year'):
        lines.append(f'  year    = {{{metadata["year"]}}},')
    if metadata.get('volume'):
        lines.append(f'  volume  = {{{metadata["volume"]}}},')
    if metadata.get('issue'):
        lines.append(f'  number  = {{{metadata["issue"]}}},')
    if metadata.get('pages'):
        pages = str(metadata['pages']).replace('-', '--')
        lines.append(f'  pages   = {{{pages}}},')
    if metadata.get('doi'):
        lines.append(f'  doi     = {{{metadata["doi"]}}},')

    # Remove trailing comma from last field
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    lines.append('}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch citation metadata from DOI, PMID, arXiv ID, or search query',
        epilog='Example: uv run fetch_metadata.py --doi 10.1038/s41586-021-03819-2',
    )
    parser.add_argument('--doi', help='Digital Object Identifier')
    parser.add_argument('--pmid', help='PubMed ID')
    parser.add_argument('--arxiv', help='arXiv ID')
    parser.add_argument('--query', help='Search query (returns multiple results)')
    parser.add_argument('--limit', type=int, default=10, help='Max search results (default: 10)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    args = parser.parse_args()

    fetcher = MetadataFetcher()

    if args.query:
        # Search mode — return list of results
        results = fetcher.search(args.query, limit=args.limit)
        if not results:
            print('No results found.', file=sys.stderr)
            sys.exit(1)
        # Add paper IDs to each result
        for r in results:
            r['id'] = generate_paper_id(r)
            r['bibtex'] = metadata_to_bibtex(r['id'], r)
        output = json.dumps({'query': args.query, 'count': len(results), 'results': results}, indent=2)

    elif args.doi or args.pmid or args.arxiv:
        # Single paper mode
        metadata = None
        if args.doi:
            metadata = fetcher.fetch_by_doi(args.doi)
        elif args.pmid:
            metadata = fetcher.fetch_by_pmid(args.pmid)
        elif args.arxiv:
            metadata = fetcher.fetch_by_arxiv(args.arxiv)

        if not metadata:
            print('Error: Could not fetch metadata.', file=sys.stderr)
            sys.exit(1)

        # If we fetched by PMID/arXiv and got a DOI, try CrossRef for richer metadata
        if not args.doi and metadata.get('doi'):
            crossref = fetcher.fetch_by_doi(metadata['doi'])
            if crossref:
                # Merge: keep original fields, fill gaps from CrossRef
                for key, val in crossref.items():
                    if val and not metadata.get(key):
                        metadata[key] = val

        paper_id = generate_paper_id(metadata)
        metadata['id'] = paper_id
        metadata['bibtex'] = metadata_to_bibtex(paper_id, metadata)

        output = json.dumps(metadata, indent=2)

    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote to {args.output}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
