#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
s2_recommendations.py — Semantic Scholar paper recommendations, deduped against ansa.

USAGE
  ./s2_recommendations.py --doi 10.1016/s0896-6273(02)00823-1
  ./s2_recommendations.py --doi 10.xxx --limit 50 --new-only -o recs.jsonl
  ./s2_recommendations.py --doi-list dois.txt --limit 30   # one DOI per line; pooled recs

Uses the /recommendations/v1/papers endpoint (no key required, rate-limited).
"""
import argparse
import os
import sys
import time
from _common import http_json, ansa_lookup_doi, write_jsonl, shorten

S2_KEY = os.environ.get("S2_API_KEY", "")
FIELDS = "title,abstract,authors,year,venue,citationCount,externalIds"


def s2_headers():
    h = {}
    if S2_KEY:
        h["x-api-key"] = S2_KEY
    return h


def normalize(p):
    ext = p.get("externalIds") or {}
    doi = (ext.get("DOI") or "").lower() or None
    return {
        "doi": doi,
        "s2_id": p.get("paperId"),
        "title": p.get("title") or "",
        "year": p.get("year"),
        "journal": p.get("venue") or "",
        "authors": [a.get("name", "") for a in (p.get("authors") or [])],
        "citation_count": p.get("citationCount"),
        "abstract": shorten(p.get("abstract") or "", 600),
    }


def get_single(doi, limit):
    url = (f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/DOI:{doi}"
           f"?limit={limit}&fields={FIELDS}")
    data = http_json(url, headers=s2_headers())
    return data.get("recommendedPapers") or []


def get_pooled(positive_dois, limit):
    body = {
        "positivePaperIds": [f"DOI:{d}" for d in positive_dois],
        "negativePaperIds": [],
    }
    url = (f"https://api.semanticscholar.org/recommendations/v1/papers"
           f"?limit={limit}&fields={FIELDS}")
    data = http_json(url, method="POST", body=body, headers=s2_headers())
    return data.get("recommendedPapers") or []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--doi", help="single seed DOI")
    src.add_argument("--doi-list", help="file with one DOI per line; pooled recommendations")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--new-only", action="store_true")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    if args.doi:
        print(f"[s2] single-seed recommendations for {args.doi}", file=sys.stderr)
        papers = get_single(args.doi.strip(), args.limit)
    else:
        with open(args.doi_list) as f:
            dois = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        print(f"[s2] pooled recommendations from {len(dois)} seed DOIs", file=sys.stderr)
        papers = get_pooled(dois, args.limit)

    out = []
    for p in papers:
        rec = normalize(p)
        aid, ck = ansa_lookup_doi(rec["doi"]) if rec["doi"] else (None, None)
        rec["in_graph"] = aid is not None
        rec["ansa_id"] = aid
        rec["ansa_citekey"] = ck
        if args.new_only and rec["in_graph"]:
            continue
        out.append(rec)
        time.sleep(0.05)  # polite
    in_g = sum(1 for r in out if r["in_graph"])
    print(f"[s2] {len(out)} records ({in_g} already in graph)", file=sys.stderr)
    write_jsonl(out, args.output)


if __name__ == "__main__":
    main()
