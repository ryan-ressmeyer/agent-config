#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Find open-access PDF URLs for a paper.
Checks Unpaywall, PubMed Central, arXiv/bioRxiv/medRxiv, and Semantic Scholar.
Does NOT download — just returns URLs for the agent to fetch.
"""

import sys
import os
import json
import argparse
import time

import requests


class OpenAccessFinder:
    """Find open-access PDF URLs from multiple sources."""

    def __init__(self, email: str = ''):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiteratureReview/1.0 (pdf-retrieve skill)'
        })
        self.email = email or os.getenv('UNPAYWALL_EMAIL', '')

    def check_unpaywall(self, doi: str) -> dict | None:
        """Check Unpaywall for open-access PDF."""
        if not self.email:
            return None
        url = f'https://api.unpaywall.org/v2/{doi}'
        params = {'email': self.email}
        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            best = data.get('best_oa_location') or {}
            pdf_url = best.get('url_for_pdf') or best.get('url')
            if pdf_url:
                return {
                    'source': 'unpaywall',
                    'pdf_url': pdf_url,
                    'version': best.get('version', 'unknown'),
                    'host_type': best.get('host_type', 'unknown'),
                    'is_oa': data.get('is_oa', False),
                }
            return None
        except Exception as e:
            print(f'Unpaywall error: {e}', file=sys.stderr)
            return None

    def check_pmc(self, pmid: str) -> dict | None:
        """Check if paper is available in PubMed Central."""
        if not pmid:
            return None
        # Use NCBI elink to find PMC ID
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
        params = {
            'dbfrom': 'pubmed',
            'db': 'pmc',
            'id': pmid,
            'retmode': 'json',
        }
        email = os.getenv('NCBI_EMAIL', '')
        if email:
            params['email'] = email
        api_key = os.getenv('NCBI_API_KEY', '')
        if api_key:
            params['api_key'] = api_key
        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            linksets = data.get('linksets', [])
            if not linksets:
                return None
            links = linksets[0].get('linksetdbs', [])
            for linkdb in links:
                if linkdb.get('dbto') == 'pmc':
                    pmc_ids = linkdb.get('links', [])
                    if pmc_ids:
                        pmc_id = pmc_ids[0]
                        return {
                            'source': 'pmc',
                            'pdf_url': f'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/',
                            'pmc_id': f'PMC{pmc_id}',
                        }
            return None
        except Exception as e:
            print(f'PMC error: {e}', file=sys.stderr)
            return None

    def check_preprint(self, arxiv_id: str = '', doi: str = '') -> dict | None:
        """Check arXiv/bioRxiv/medRxiv for PDF."""
        if arxiv_id:
            return {
                'source': 'arxiv',
                'pdf_url': f'https://arxiv.org/pdf/{arxiv_id}.pdf',
            }
        # Check if DOI is from bioRxiv or medRxiv
        if doi:
            if '10.1101/' in doi:
                return {
                    'source': 'biorxiv/medrxiv',
                    'pdf_url': f'https://www.biorxiv.org/content/{doi}v1.full.pdf',
                }
        return None

    def check_semantic_scholar(self, doi: str) -> dict | None:
        """Check Semantic Scholar for open-access PDF link."""
        url = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}'
        params = {'fields': 'openAccessPdf'}
        api_key = os.getenv('S2_API_KEY', '')
        headers = {}
        if api_key:
            headers['x-api-key'] = api_key
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            oa = data.get('openAccessPdf')
            if oa and oa.get('url'):
                return {
                    'source': 'semantic-scholar',
                    'pdf_url': oa['url'],
                    'status': oa.get('status', 'unknown'),
                }
            return None
        except Exception as e:
            print(f'Semantic Scholar error: {e}', file=sys.stderr)
            return None

    def find_all(self, doi: str, pmid: str = '', arxiv_id: str = '') -> dict:
        """Check all sources and return results."""
        found = []
        best = None

        # 1. Unpaywall (highest quality — legal OA)
        result = self.check_unpaywall(doi)
        if result:
            found.append(result)
            if not best:
                best = result
        time.sleep(0.2)

        # 2. PMC
        result = self.check_pmc(pmid)
        if result:
            found.append(result)
            if not best:
                best = result
        time.sleep(0.2)

        # 3. Preprint servers
        result = self.check_preprint(arxiv_id=arxiv_id, doi=doi)
        if result:
            found.append(result)
            if not best:
                best = result

        # 4. Semantic Scholar
        result = self.check_semantic_scholar(doi)
        if result:
            found.append(result)
            if not best:
                best = result

        return {
            'doi': doi,
            'doi_url': f'https://doi.org/{doi}',
            'sources_checked': ['unpaywall', 'pmc', 'preprint', 'semantic-scholar'],
            'found': found,
            'best': best,
            'open_access_available': len(found) > 0,
        }


def main():
    parser = argparse.ArgumentParser(
        description='Find open-access PDF URLs for a paper',
        epilog='Example: uv run find_open_access.py --doi 10.1038/s41586-021-03819-2 --email user@uni.edu',
    )
    parser.add_argument('--doi', required=True, help='DOI of the paper')
    parser.add_argument('--pmid', default='', help='PubMed ID (improves PMC lookup)')
    parser.add_argument('--arxiv', default='', help='arXiv ID (direct PDF available)')
    parser.add_argument('--email', default='', help='Email for Unpaywall API (or set UNPAYWALL_EMAIL)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    args = parser.parse_args()

    finder = OpenAccessFinder(email=args.email)
    results = finder.find_all(doi=args.doi, pmid=args.pmid, arxiv_id=args.arxiv)

    output = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote results to {args.output}', file=sys.stderr)
    else:
        print(output)

    # Human-readable summary to stderr
    if results['open_access_available']:
        print(f'\nOpen access found! Best URL: {results["best"]["pdf_url"]}', file=sys.stderr)
        print(f'Source: {results["best"]["source"]}', file=sys.stderr)
    else:
        print(f'\nNo open-access PDF found.', file=sys.stderr)
        print(f'DOI link: {results["doi_url"]}', file=sys.stderr)
        print('The user will need to retrieve this paper manually.', file=sys.stderr)


if __name__ == '__main__':
    main()
